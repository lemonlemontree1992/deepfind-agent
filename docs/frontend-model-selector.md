# 前端模型选择集成指南

## 📍 集成位置

在 DeepFind Agent 界面的设置面板或工具栏中添加模型选择下拉框。

```
┌──────────────────────────────────────────────┐
│  🔍 DeepFind Agent          [⚙️设置]         │
├──────────────────────────────────────────────┤
│                                              │
│  🤖 AI 模型: [ DeepSeek ▼ ]                  │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  请输入您的调研主题...                  │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  [发送]                                      │
└──────────────────────────────────────────────┘
```

---

## 🎯 实施步骤

### 步骤 1: 创建模型选择组件

**文件**: `frontend/src/components/ModelSelector.tsx`

```tsx
import { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Sparkles, Zap, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface ModelInfo {
  name: string;
  model: string;
  configured: boolean;
  description: string;
}

interface ModelSelectorProps {
  onModelChange?: (model: string) => void;
  className?: string;
}

export function ModelSelector({ onModelChange, className = '' }: ModelSelectorProps) {
  const [currentModel, setCurrentModel] = useState<string>('deepseek');
  const [availableModels, setAvailableModels] = useState<Record<string, ModelInfo>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // 初始化时获取当前设置
  useEffect(() => {
    fetch('/api/settings')
      .then(res => res.json())
      .then(data => {
        setCurrentModel(data.llmProvider);
        setAvailableModels(data.availableProviders);
        setIsInitialized(true);
      })
      .catch(error => {
        console.error('Failed to fetch settings:', error);
        toast.error('获取模型设置失败');
      });
  }, []);

  // 切换模型
  const handleModelChange = async (value: string) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llmProvider: value }),
      });

      const data = await response.json();

      if (data.success) {
        setCurrentModel(value);
        toast.success(data.message || `已切换到 ${value.toUpperCase()} 模型`);
        onModelChange?.(value);
      } else {
        toast.error(data.detail || '模型切换失败');
      }
    } catch (error) {
      console.error('Failed to change model:', error);
      toast.error('模型切换失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isInitialized) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        <span className="text-sm text-muted-foreground">加载中...</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <label className="text-sm font-medium text-muted-foreground">AI 模型</label>
      <Select 
        value={currentModel} 
        onValueChange={handleModelChange}
        disabled={isLoading}
      >
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="选择模型" />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(availableModels).map(([key, info]) => (
            <SelectItem 
              key={key} 
              value={key}
              disabled={!info.configured}
            >
              <div className="flex items-center gap-2">
                {key === 'deepseek' ? (
                  <Sparkles className="h-4 w-4 text-blue-500" />
                ) : (
                  <Zap className="h-4 w-4 text-green-500" />
                )}
                <div className="flex-1">
                  <div className="font-medium">{info.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {info.description}
                  </div>
                </div>
                {!info.configured && (
                  <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">
                    未配置
                  </span>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {isLoading && (
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      )}
    </div>
  );
}
```

---

### 步骤 2: 集成到主界面

**文件**: `frontend/src/pages/Index.tsx`

找到合适的位置添加模型选择器，建议添加在页面顶部的工具栏区域。

```tsx
import { ModelSelector } from '@/components/ModelSelector';

// 在页面顶部工具栏区域添加
<div className="flex items-center justify-between">
  <h1 className="text-xl font-semibold">🔍 DeepFind Agent</h1>
  
  <div className="flex items-center gap-4">
    {/* 模型选择器 */}
    <ModelSelector 
      onModelChange={(model) => {
        console.log('Model changed to:', model);
        // 可以添加额外的处理逻辑
      }}
    />
    
    {/* 其他工具按钮 */}
    <Button variant="ghost" size="sm">
      <Settings className="h-4 w-4" />
    </Button>
  </div>
</div>
```

---

### 步骤 3: 更新设置上下文

**文件**: `frontend/src/contexts/SettingsContext.tsx`

```tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast } from 'sonner';

interface ModelInfo {
  name: string;
  model: string;
  configured: boolean;
  description: string;
}

interface Settings {
  llmProvider: 'deepseek' | 'glm';
  availableProviders: Record<string, ModelInfo>;
  language: 'zh' | 'en';
}

interface SettingsContextType {
  settings: Settings;
  setLLMProvider: (provider: 'deepseek' | 'glm') => Promise<void>;
  setLanguage: (language: 'zh' | 'en') => void;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>({
    llmProvider: 'deepseek',
    availableProviders: {},
    language: 'zh',
  });

  // 获取设置
  const refreshSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      
      setSettings(prev => ({
        ...prev,
        llmProvider: data.llmProvider,
        availableProviders: data.availableProviders,
      }));
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  // 初始化
  useEffect(() => {
    refreshSettings();
  }, []);

  // 切换模型
  const setLLMProvider = async (provider: 'deepseek' | 'glm') => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llmProvider: provider }),
      });

      const data = await response.json();

      if (data.success) {
        setSettings(prev => ({
          ...prev,
          llmProvider: provider,
        }));
        toast.success(data.message);
      } else {
        toast.error(data.detail || '切换失败');
      }
    } catch (error) {
      toast.error('切换失败，请重试');
      throw error;
    }
  };

  // 切换语言
  const setLanguage = (language: 'zh' | 'en') => {
    setSettings(prev => ({ ...prev, language }));
  };

  return (
    <SettingsContext.Provider value={{ settings, setLLMProvider, setLanguage, refreshSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within SettingsProvider');
  }
  return context;
}
```

---

### 步骤 4: 添加设置面板组件（可选）

**文件**: `frontend/src/components/SettingsPanel.tsx`

```tsx
import { useState } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Settings, Sparkles, Zap, Check } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';

export function SettingsPanel() {
  const { settings, setLLMProvider } = useSettings();
  const [isOpen, setIsOpen] = useState(false);

  const handleModelChange = async (value: string) => {
    await setLLMProvider(value as 'deepseek' | 'glm');
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>设置</SheetTitle>
          <SheetDescription>
            配置 DeepFind Agent 的运行参数
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* AI 模型选择 */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium">AI 模型</h3>
            <RadioGroup
              value={settings.llmProvider}
              onValueChange={handleModelChange}
              className="space-y-3"
            >
              {/* DeepSeek 选项 */}
              <div className="flex items-start space-x-3 p-4 rounded-lg border hover:bg-accent cursor-pointer">
                <RadioGroupItem value="deepseek" id="deepseek" />
                <Label htmlFor="deepseek" className="flex-1 cursor-pointer">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-blue-500" />
                    <span className="font-medium">DeepSeek</span>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                      推荐
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    推理能力强，适合深度研究和复杂分析任务
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <span>⚡ 速度：中等</span>
                    <span>💰 成本：¥1/百万token</span>
                  </div>
                </Label>
                {settings.llmProvider === 'deepseek' && (
                  <Check className="h-4 w-4 text-primary mt-1" />
                )}
              </div>

              {/* GLM 选项 */}
              <div className="flex items-start space-x-3 p-4 rounded-lg border hover:bg-accent cursor-pointer">
                <RadioGroupItem 
                  value="glm" 
                  id="glm"
                  disabled={!settings.availableProviders?.glm?.configured}
                />
                <Label htmlFor="glm" className="flex-1 cursor-pointer">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-500" />
                    <span className="font-medium">GLM-5.2</span>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                      快速
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    响应速度快，成本低，适合日常查询和快速响应
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <span>⚡ 速度：极快</span>
                    <span>💰 成本：¥0.1/百万token</span>
                  </div>
                  {!settings.availableProviders?.glm?.configured && (
                    <div className="mt-2 text-xs bg-red-50 text-red-600 px-3 py-1.5 rounded">
                      ⚠️ 需要在 .env 中配置 GLM_API_KEY
                    </div>
                  )}
                </Label>
                {settings.llmProvider === 'glm' && (
                  <Check className="h-4 w-4 text-primary mt-1" />
                )}
              </div>
            </RadioGroup>
          </div>

          {/* 使用建议 */}
          <div className="space-y-2 p-4 bg-muted/50 rounded-lg">
            <h4 className="text-sm font-medium">💡 使用建议</h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>• <strong>深度研究</strong>：使用 DeepSeek，推理能力更强</li>
              <li>• <strong>快速查询</strong>：使用 GLM-5.2，响应更快</li>
              <li>• <strong>成本优化</strong>：GLM-5.2 成本仅为 DeepSeek 的 1/10</li>
            </ul>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

---

### 步骤 5: 样式优化

确保 Select 组件有合适的样式，可以使用 Shadcn UI 的样式：

**文件**: `frontend/src/components/ui/select.tsx`（如果不存在）

```tsx
import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { Check, ChevronDown, ChevronUp } from "lucide-react"

import { cn } from "@/lib/utils"

const Select = SelectPrimitive.Root

const SelectGroup = SelectPrimitive.Group

const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown className="h-4 w-4 opacity-50" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectScrollUpButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollUpButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollUpButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollUpButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronUp className="h-4 w-4" />
  </SelectPrimitive.ScrollUpButton>
))
SelectScrollUpButton.displayName = SelectPrimitive.ScrollUpButton.displayName

const SelectScrollDownButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollDownButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollDownButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollDownButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronDown className="h-4 w-4" />
  </SelectPrimitive.ScrollDownButton>
))
SelectScrollDownButton.displayName =
  SelectPrimitive.ScrollDownButton.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        "relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        position === "popper" &&
          "data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1",
        className
      )}
      position={position}
      {...props}
    >
      <SelectScrollUpButton />
      <SelectPrimitive.Viewport
        className={cn(
          "p-1",
          position === "popper" &&
            "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"
        )}
      >
        {children}
      </SelectPrimitive.Viewport>
      <SelectScrollDownButton />
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectLabel = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Label>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={cn("py-1.5 pl-8 pr-2 text-sm font-semibold", className)}
    {...props}
  />
))
SelectLabel.displayName = SelectPrimitive.Label.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    <span className="absolute right-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <Check className="h-4 w-4" />
      </SelectPrimitive.ItemIndicator>
    </span>
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

const SelectSeparator = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-muted", className)}
    {...props}
  />
))
SelectSeparator.displayName = SelectPrimitive.Separator.displayName

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
}
```

---

## 🎨 界面效果预览

### 简洁版（下拉框）

```
┌────────────────────────────────────────┐
│  🔍 DeepFind Agent                     │
│                                        │
│  AI 模型: [ DeepSeek ▼ ]               │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  请输入您的调研主题...            │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### 完整版（设置面板）

```
┌────────────────────────────────────────┐
│  设置                            [×]   │
├────────────────────────────────────────┤
│                                        │
│  AI 模型                               │
│                                        │
│  ○ DeepSeek  推荐                      │
│    ⚝ 推理能力强，适合深度研究          │
│    ⚡ 速度：中等  💰 成本：¥1/百万token │
│                                        │
│  ● GLM-5.2  快速                       │
│    ⚝ 响应速度快，适合日常查询          │
│    ⚡ 速度：极快  💰 成本：¥0.1/百万token│
│                                        │
│  💡 使用建议                           │
│  • 深度研究：使用 DeepSeek            │
│  • 快速查询：使用 GLM-5.2             │
│  • 成本优化：GLM 成本仅为 DeepSeek 1/10│
│                                        │
└────────────────────────────────────────┘
```

---

## 📝 测试清单

完成集成后，请测试以下功能：

- [ ] 下拉框正确显示当前模型
- [ ] 切换模型后状态更新
- [ ] 切换成功显示 Toast 提示
- [ ] 未配置的模型显示禁用状态
- [ ] 发送查询时使用正确的模型
- [ ] 页面刷新后设置保持

---

**预计时间**: 前端集成约 30-40 分钟