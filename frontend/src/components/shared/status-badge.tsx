import { Badge } from "@/components/ui/badge";
import { BookingStatus } from "@/types/booking";
import { cn } from "@/lib/utils/cn";

interface StatusBadgeProps {
  status: BookingStatus;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const statusConfig: Record<
  BookingStatus,
  { label: string; variant: "default" | "secondary" | "success" | "warning" | "error" | "info" }
> = {
  requested: { label: "Requested", variant: "info" },
  accepted: { label: "Accepted", variant: "info" },
  scheduled: { label: "Scheduled", variant: "info" },
  in_progress: { label: "In Progress", variant: "warning" },
  completed: { label: "Completed", variant: "success" },
  cancelled: { label: "Cancelled", variant: "error" },
  disputed: { label: "Disputed", variant: "warning" },
};

export function StatusBadge({ status, size = "md", className }: StatusBadgeProps) {
  const config = statusConfig[status];
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-0.5",
    lg: "text-base px-3 py-1",
  };

  return (
    <Badge
      variant={config.variant}
      className={cn(sizeClasses[size], className)}
    >
      {config.label}
    </Badge>
  );
}
