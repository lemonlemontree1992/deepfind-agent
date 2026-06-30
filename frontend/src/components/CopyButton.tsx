import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface CopyButtonProps {
  text: string;
  className?: string;
}

export const CopyButton: React.FC<CopyButtonProps> = ({ text, className = '' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation(); // 防止触发父元素事件
    e.preventDefault();

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success('✓ 已复制到剪贴板', {
        duration: 2000,
        position: 'top-center',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('复制失败:', err);
      toast.error('复制失败，请重试');
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      className={`
        h-8 px-3 gap-1.5
        bg-background hover:bg-accent
        border-2 border-border hover:border-primary
        shadow-sm hover:shadow
        transition-all duration-200
        ${copied ? 'bg-green-50 border-green-500 hover:bg-green-50 hover:border-green-500' : ''}
        ${className}
      `}
      onClick={handleCopy}
      title={copied ? '已复制 ✓' : '一键复制全部内容'}
    >
      {copied ? (
        <>
          <Check className="h-4 w-4 text-green-600" />
          <span className="text-xs font-medium text-green-600">已复制</span>
        </>
      ) : (
        <>
          <Copy className="h-4 w-4 text-foreground" />
          <span className="text-xs font-medium">复制</span>
        </>
      )}
    </Button>
  );
};