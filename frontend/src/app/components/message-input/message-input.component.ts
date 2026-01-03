import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ChatService } from '../../services/chat.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-message-input',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatButtonModule],
  templateUrl: './message-input.component.html',
  styleUrl: './message-input.component.scss'
})
export class MessageInputComponent {
  private chatService = inject(ChatService);
  private apiService = inject(ApiService);

  message = signal('');
  isInitialized = this.apiService.isInitialized;
  isThinking = this.chatService.isThinking;

  async sendMessage() {
    const msg = this.message().trim();
    if (!msg || this.isThinking()) return;

    this.message.set('');
    await this.chatService.sendMessage(msg);
  }

  onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
