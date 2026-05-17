"use client";

import { useToast } from "@/hooks/use-toast";
import { AxiosError } from "axios";

export function useApiError() {
  const { toast } = useToast();

  function catchError(error: unknown, fallback?: { title?: string; description?: string }) {
    const title = fallback?.title || "请求失败";
    let description = fallback?.description || "请稍后重试";

    if (error instanceof AxiosError) {
      description = error.response?.data?.detail || error.message || description;
    } else if (error instanceof Error) {
      description = error.message || description;
    }

    toast({
      variant: "destructive",
      title,
      description,
    });
  }

  return { catchError };
}
