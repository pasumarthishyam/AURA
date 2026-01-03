import { Injectable, signal, inject } from '@angular/core';
import { ApiService, ChatResponse } from './api.service';

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    success?: boolean;
    trace?: any[];
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

    async sendMessage(content: string): Promise<void> {
        // Add user message
        const userMsg: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content,
            timestamp: new Date()
        };
        this.messages.update(msgs => [...msgs, userMsg]);

        // Show thinking
        this.isThinking.set(true);
        this.error.set(null);

        try {
            const response = await this.apiService.sendMessage(content);

            // Add assistant message
            const assistantMsg: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.message,
                timestamp: new Date(),
                success: response.success,
                trace: response.trace
            };
            this.messages.update(msgs => [...msgs, assistantMsg]);

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
            this.error.set({
                message: err?.message || 'An unexpected error occurred'
            });
        } finally {
            this.isThinking.set(false);
        }
    }

    clearError(): void {
        this.error.set(null);
    }

    clearMessages(): void {
        this.messages.set([]);
        this.error.set(null);
    }
}
