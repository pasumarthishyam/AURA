import { Injectable, signal, inject } from '@angular/core';
import { ApiService, ChatResponse } from './api.service';

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    displayContent: string;  // For typewriter effect
    timestamp: Date;
    success?: boolean;
    trace?: any[];
    isStreaming?: boolean;  // Indicates if message is still being "typed"
}

export interface ErrorInfo {
    message: string;
    trace?: string;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    private apiService = inject(ApiService);

    messages = signal<Message[]>([]);
    isThinking = signal(false);
    error = signal<ErrorInfo | null>(null);

    // Typewriter speed (ms per character)
    private typewriterSpeed = 15;

    async sendMessage(content: string): Promise<void> {
        // Add user message
        const userMsg: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content,
            displayContent: content,
            timestamp: new Date()
        };
        this.messages.update(msgs => [...msgs, userMsg]);

        // Show thinking
        this.isThinking.set(true);
        this.error.set(null);

        try {
            const response = await this.apiService.sendMessage(content);

            // Add assistant message with empty displayContent initially
            const assistantMsg: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.message,
                displayContent: '',  // Start empty for typewriter
                timestamp: new Date(),
                success: response.success,
                trace: response.trace,
                isStreaming: true
            };
            this.messages.update(msgs => [...msgs, assistantMsg]);

            // Stop thinking indicator once we start typing
            this.isThinking.set(false);

            // Start typewriter effect
            await this.typewriterEffect(assistantMsg.id, response.message);

            // Show error if not successful
            if (!response.success && response.trace?.length) {
                const lastError = response.trace.find(t => t.error);
                if (lastError) {
                    this.error.set({
                        message: response.message,
                        trace: lastError.error || undefined
                    });
                }
            }
        } catch (err: any) {
            this.isThinking.set(false);
            this.error.set({
                message: err?.message || 'An unexpected error occurred'
            });
        }
    }

    /**
     * Typewriter effect - reveals text character by character
     */
    private async typewriterEffect(messageId: string, fullText: string): Promise<void> {
        const chars = fullText.split('');
        let currentIndex = 0;

        return new Promise((resolve) => {
            const interval = setInterval(() => {
                currentIndex++;

                this.messages.update(msgs =>
                    msgs.map(msg => {
                        if (msg.id === messageId) {
                            return {
                                ...msg,
                                displayContent: fullText.substring(0, currentIndex),
                                isStreaming: currentIndex < chars.length
                            };
                        }
                        return msg;
                    })
                );

                if (currentIndex >= chars.length) {
                    clearInterval(interval);
                    resolve();
                }
            }, this.typewriterSpeed);
        });
    }

    clearError(): void {
        this.error.set(null);
    }

    clearMessages(): void {
        this.messages.set([]);
        this.error.set(null);
    }
}
