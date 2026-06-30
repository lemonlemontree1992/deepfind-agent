import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { toast } from "sonner";

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const exportToPDF = async (elementId: string, filename: string = "conversation.pdf"): Promise<boolean> => {
  const element = document.getElementById(elementId);
  if (!element) {
    toast.error("导出失败", { description: "找不到要导出的内容" });
    return false;
  }

  try {
    toast.loading("正在生成 PDF...", { id: "pdf-export" });

    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: "#ffffff",
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
      onclone: (clonedDoc) => {
        const clonedElement = clonedDoc.getElementById(elementId);
        if (clonedElement) {
          clonedElement.style.height = 'auto';
          clonedElement.style.overflow = 'visible';
        }
      }
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "px",
      format: [canvas.width, canvas.height]
    });

    pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
    pdf.save(filename);

    toast.success("PDF 导出成功", { id: "pdf-export" });
    return true;
  } catch (error) {
    console.error("PDF export failed:", error);
    toast.error("PDF 导出失败", {
      id: "pdf-export",
      description: error instanceof Error ? error.message : "请稍后重试"
    });
    return false;
  }
};
