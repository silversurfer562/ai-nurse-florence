import { clsx } from 'clsx'
import { Activity, FileText, Home, Stethoscope } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
  },
  {
    name: 'Wizards',
    href: '/wizards',
    icon: FileText,
  },
  {
    name: 'Clinical Tools',
    href: '/clinical',
    icon: Stethoscope,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: Activity,
  },
]

export function Navigation() {
  const location = useLocation()

  return (
    <nav className="flex space-x-8">
      {navigationItems.map((item) => {
        const isActive = location.pathname === item.href ||
          (item.href !== '/' && location.pathname.startsWith(item.href))

        return (
          <Link
            key={item.name}
            to={item.href}
            className={clsx(
              'inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              isActive
                ? 'bg-clinical-100 text-clinical-700 border border-clinical-200'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
            )}
          >
            <item.icon className="w-4 h-4 mr-2" />
            {item.name}
          </Link>
        )
      })}
    </nav>
  )
}
