import { format, formatDistance, isToday, isTomorrow, isYesterday, parseISO } from "date-fns";

/**
 * Format date to readable string
 */
export function formatDate(date: Date | string, formatStr: string = "PPP"): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, formatStr);
}

/**
 * Format date relative to now
 */
export function formatRelativeDate(date: Date | string): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  
  if (isToday(dateObj)) {
    return "Today";
  }
  
  if (isTomorrow(dateObj)) {
    return "Tomorrow";
  }
  
  if (isYesterday(dateObj)) {
    return "Yesterday";
  }
  
  return formatDistance(dateObj, new Date(), { addSuffix: true });
}

/**
 * Format date and time
 */
export function formatDateTime(date: Date | string): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, "PPp");
}

/**
 * Format time only
 */
export function formatTime(date: Date | string): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, "h:mm a");
}
