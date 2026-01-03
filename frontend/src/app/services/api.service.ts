import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface InitResponse {
    success: boolean;
    message: string;
}

export interface ChatResponse {
    success: boolean;
    message: string;
    trace: TraceStep[];
}

export interface TraceStep {
    step_id: number;
    action: any;
    success: boolean;
    result: string | null;
    observation: string | null;
    error: string | null;
    timestamp: number;
}

export interface StatusResponse {
    initialized: boolean;
    gpu: string;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private baseUrl = 'http://localhost:8000/api';

    isInitialized = signal(false);
    gpuStatus = signal('Not active');

    constructor(private http: HttpClient) {
        this.checkStatus();
    }

    async checkStatus(): Promise<StatusResponse> {
        try {
            const response = await firstValueFrom(
                this.http.get<StatusResponse>(`${this.baseUrl}/status`)
            );
            this.isInitialized.set(response.initialized);
            this.gpuStatus.set(response.gpu);
            return response;
        } catch (error) {
            console.error('Failed to check status:', error);
            return { initialized: false, gpu: 'Error' };
        }
    }

    async initialize(): Promise<InitResponse> {
        try {
            const response = await firstValueFrom(
                this.http.post<InitResponse>(`${this.baseUrl}/initialize`, {})
            );
            if (response.success) {
                this.isInitialized.set(true);
            }
            return response;
        } catch (error: any) {
            return {
                success: false,
                message: error?.message || 'Failed to initialize'
            };
        }
    }

    async sendMessage(message: string): Promise<ChatResponse> {
        try {
            return await firstValueFrom(
                this.http.post<ChatResponse>(`${this.baseUrl}/chat`, { message })
            );
        } catch (error: any) {
            return {
                success: false,
                message: error?.error?.detail || error?.message || 'Request failed',
                trace: []
            };
        }
    }
}
