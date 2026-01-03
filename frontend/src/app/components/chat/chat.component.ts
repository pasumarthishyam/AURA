import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ChatService, Message } from '../../services/chat.service';
import { ErrorDisplayComponent } from '../error-display/error-display.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, MatIconModule, ErrorDisplayComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  private chatService = inject(ChatService);

  messages = this.chatService.messages;
  isThinking = this.chatService.isThinking;
  error = this.chatService.error;

  clearError() {
    this.chatService.clearError();
  }

  /**
   * Send a suggestion chip as a message
   */
  sendSuggestion(suggestion: string) {
    this.chatService.sendMessage(suggestion);
  }
}

