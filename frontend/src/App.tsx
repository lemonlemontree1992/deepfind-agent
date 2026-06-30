import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as SonnerToaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HashRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { SettingsProvider } from "@/contexts/SettingsContext";
import NotFound from "./pages/NotFound";

import Index from "./pages/Index";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <LanguageProvider>
      <SettingsProvider>
        <TooltipProvider>
          <Toaster />
          <SonnerToaster position="top-right" richColors />
          <HashRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </HashRouter>
        </TooltipProvider>
      </SettingsProvider>
    </LanguageProvider>
  </QueryClientProvider>
);

export default App;