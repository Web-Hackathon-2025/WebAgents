import { Star } from "lucide-react";
import { cn } from "@/lib/utils/cn";

interface RatingDisplayProps {
  rating: number;
  count?: number;
  size?: "sm" | "md" | "lg";
  showCount?: boolean;
  className?: string;
}

export function RatingDisplay({
  rating,
  count,
  size = "md",
  showCount = true,
  className,
}: RatingDisplayProps) {
  const sizeClasses = {
    sm: "h-3 w-3",
    md: "h-4 w-4",
    lg: "h-5 w-5",
  };

  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;

  return (
    <div className={cn("flex items-center gap-1", className)}>
      <div className="flex items-center">
        {Array.from({ length: 5 }).map((_, index) => {
          if (index < fullStars) {
            return (
              <Star
                key={index}
                className={cn(sizeClasses[size], "fill-warning text-warning")}
              />
            );
          }
          if (index === fullStars && hasHalfStar) {
            return (
              <Star
                key={index}
                className={cn(sizeClasses[size], "fill-warning/50 text-warning")}
              />
            );
          }
          return (
            <Star
              key={index}
              className={cn(sizeClasses[size], "text-gray-300")}
            />
          );
        })}
      </div>
      {showCount && count !== undefined && (
        <span className="text-sm text-text-secondary">
          {rating.toFixed(1)} ({count})
        </span>
      )}
      {showCount && count === undefined && (
        <span className="text-sm text-text-secondary">{rating.toFixed(1)}</span>
      )}
    </div>
  );
}
