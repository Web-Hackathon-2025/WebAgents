/**
 * Real-time features using Server-Sent Events (SSE) or WebSocket
 */

export class RealtimeClient {
  private eventSource: EventSource | null = null;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(
    private url: string,
    private useWebSocket: boolean = false
  ) {}

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.useWebSocket) {
      this.connectWebSocket(onMessage, onError);
    } else {
      this.connectSSE(onMessage, onError);
    }
  }

  private connectSSE(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    this.eventSource = new EventSource(this.url);

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
        this.reconnectAttempts = 0; // Reset on successful message
      } catch (error) {
        console.error("Failed to parse SSE message:", error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      if (onError) {
        onError(error);
      }

      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => {
          this.disconnect();
          this.connectSSE(onMessage, onError);
        }, this.reconnectDelay * this.reconnectAttempts);
      }
    };
  }

  private connectWebSocket(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    this.ws = new WebSocket(this.url);

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
        this.reconnectAttempts = 0;
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (onError) {
        onError(error);
      }
    };

    this.ws.onclose = () => {
      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => {
          this.connectWebSocket(onMessage, onError);
        }, this.reconnectDelay * this.reconnectAttempts);
      }
    };
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.reconnectAttempts = 0;
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn("WebSocket is not connected");
    }
  }
}

import { useState, useEffect } from "react";

/**
 * Hook for real-time booking status updates
 */
export function useBookingStatusUpdates(bookingId: string | null) {
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!bookingId) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const realtimeClient = new RealtimeClient(
      `${apiUrl}/bookings/${bookingId}/status/stream`
    );

    realtimeClient.connect((data) => {
      if (data.status) {
        setStatus(data.status);
      }
    });

    return () => {
      realtimeClient.disconnect();
    };
  }, [bookingId]);

  return status;
}
