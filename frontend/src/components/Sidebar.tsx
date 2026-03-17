import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  TrendingUp,
  ShieldAlert,
  ShoppingCart,
} from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/forecast", label: "Demand Forecast", icon: TrendingUp },
  { to: "/loss-prevention", label: "Loss Prevention", icon: ShieldAlert },
  { to: "/replenishment", label: "Replenishment", icon: ShoppingCart },
];

export default function Sidebar() {
  return (
    <aside className="w-60 min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
      <div className="px-6 py-5 border-b border-gray-800">
        <span className="text-lg font-semibold tracking-tight text-white">
          Retail<span className="text-brand-500"> AI</span>
        </span>
        <p className="text-xs text-gray-500 mt-0.5">Inventory Intelligence</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-brand-500/15 text-brand-500 font-medium"
                  : "text-gray-400 hover:text-gray-100 hover:bg-gray-800"
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-4 border-t border-gray-800">
        <p className="text-xs text-gray-600">H&amp;M Dataset · 31.7M rows</p>
      </div>
    </aside>
  );
}
