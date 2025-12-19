export const SERVICE_CATEGORIES = [
  {
    id: "plumbing",
    name: "Plumbing",
    icon: "🔧",
    description: "Plumbing repairs, installations, and maintenance",
  },
  {
    id: "electrical",
    name: "Electrical",
    icon: "⚡",
    description: "Electrical work, wiring, and repairs",
  },
  {
    id: "carpentry",
    name: "Carpentry",
    icon: "🪚",
    description: "Woodwork, furniture, and carpentry services",
  },
  {
    id: "painting",
    name: "Painting",
    icon: "🎨",
    description: "Interior and exterior painting services",
  },
  {
    id: "cleaning",
    name: "Cleaning",
    icon: "🧹",
    description: "House cleaning and maintenance services",
  },
  {
    id: "hvac",
    name: "HVAC",
    icon: "❄️",
    description: "Heating, ventilation, and air conditioning",
  },
  {
    id: "landscaping",
    name: "Landscaping",
    icon: "🌳",
    description: "Garden and landscaping services",
  },
  {
    id: "general-repair",
    name: "General Repair",
    icon: "🔨",
    description: "General home repair and maintenance",
  },
] as const;

export type ServiceCategoryId = typeof SERVICE_CATEGORIES[number]["id"];
