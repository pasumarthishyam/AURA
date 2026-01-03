import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

export interface ErrorInfo {
  message: string;
  trace?: string;
}

@Component({
  selector: 'app-error-display',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule],
  templateUrl: './error-display.component.html',
  styleUrl: './error-display.component.scss'
})
export class ErrorDisplayComponent {
  @Input() error!: ErrorInfo;
  @Output() dismiss = new EventEmitter<void>();

  showTrace = signal(false);

  toggleTrace() {
    this.showTrace.update(v => !v);
  }

  copyError() {
    const text = this.error.trace
      ? `${this.error.message}\n\n${this.error.trace}`
      : this.error.message;
    navigator.clipboard.writeText(text);
  }

  askGoogle() {
    const query = encodeURIComponent(this.error.message);
    window.open(`https://www.google.com/search?q=${query}`, '_blank');
  }

  askChatGPT() {
    const query = encodeURIComponent(`Help me fix this error: ${this.error.message}`);
    window.open(`https://chat.openai.com/?q=${query}`, '_blank');
  }
}
