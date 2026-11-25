import { useState, useCallback } from 'react';
import { briefingsApi } from '../services/api';

interface UseExportPdfResult {
  exportPdf: (briefingId: string, token: string) => Promise<void>;
  isExporting: boolean;
  error: string | null;
}

export function useExportPdf(): UseExportPdfResult {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportPdf = useCallback(async (briefingId: string, token: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const blob = await briefingsApi.exportPdf(briefingId, token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `briefing-${briefingId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message ?? 'Xuất PDF thất bại');
    } finally {
      setIsExporting(false);
    }
  }, []);

  return { exportPdf, isExporting, error };
}
