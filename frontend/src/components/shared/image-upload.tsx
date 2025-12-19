"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { FILE_UPLOAD } from "@/lib/constants/config";
import { validateFileSize, validateFileType } from "@/lib/utils/validation";
import { formatFileSize } from "@/lib/utils/format";

interface ImageUploadProps {
  maxFiles?: number;
  maxSize?: number; // MB
  accept?: string[];
  onUpload: (files: File[]) => void;
  existingImages?: string[];
  onRemove?: (index: number) => void;
  className?: string;
}

export function ImageUpload({
  maxFiles = 5,
  maxSize = FILE_UPLOAD.MAX_SIZE_MB,
  accept = FILE_UPLOAD.ALLOWED_IMAGE_TYPES,
  onUpload,
  existingImages = [],
  onRemove,
  className,
}: ImageUploadProps) {
  const [previews, setPreviews] = useState<string[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const validFiles: File[] = [];
    const newPreviews: string[] = [];

    fileArray.forEach((file) => {
      if (!validateFileType(file, accept)) {
        alert(`${file.name} is not a valid image type`);
        return;
      }

      if (!validateFileSize(file, maxSize)) {
        alert(`${file.name} exceeds maximum size of ${maxSize}MB`);
        return;
      }

      validFiles.push(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          newPreviews.push(e.target.result as string);
          if (newPreviews.length === validFiles.length) {
            setPreviews((prev) => [...prev, ...newPreviews]);
          }
        }
      };
      reader.readAsDataURL(file);
    });

    if (validFiles.length > 0) {
      onUpload(validFiles);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const removePreview = (index: number) => {
    setPreviews((prev) => prev.filter((_, i) => i !== index));
    if (onRemove) {
      onRemove(index);
    }
  };

  const allImages = [...existingImages, ...previews];
  const canAddMore = allImages.length < maxFiles;

  return (
    <div className={cn("space-y-4", className)}>
      {canAddMore && (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            dragActive
              ? "border-primary bg-primary-light/10"
              : "border-border hover:border-primary/50"
          )}
        >
          <ImageIcon className="mx-auto h-12 w-12 text-text-secondary mb-4" />
          <p className="text-sm text-text-secondary mb-2">
            Drag and drop images here, or click to select
          </p>
          <p className="text-xs text-text-secondary mb-4">
            Max {maxFiles} files, {maxSize}MB each
          </p>
          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="mr-2 h-4 w-4" />
            Select Images
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={accept.join(",")}
            onChange={(e) => handleFiles(e.target.files)}
            className="hidden"
          />
        </div>
      )}

      {allImages.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {allImages.map((image, index) => (
            <div key={index} className="relative group">
              <img
                src={image}
                alt={`Upload ${index + 1}`}
                className="w-full h-32 object-cover rounded-lg"
              />
              <button
                type="button"
                onClick={() => removePreview(index)}
                className="absolute top-2 right-2 p-1 bg-error text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
