import { useEffect, useState } from "react";

const FALLBACK_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export function useApiBaseUrl() {
  const [baseUrl, setBaseUrl] = useState(FALLBACK_BASE_URL);

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_API_BASE_URL) {
      return;
    }

    if (typeof window !== "undefined") {
      const { protocol, hostname } = window.location;
      setBaseUrl(`${protocol}//${hostname}:8000`);
    }
  }, []);

  return baseUrl;
}


