import {
    ArrowRight,
    BookOpen,
    Calendar,
    CheckCircle,
    Clock,
    FileText,
    Heart,
    Pill,
    Users
} from 'lucide-react'
import { Link } from 'react-router-dom'

const wizards = [
  {
    id: 'sbar',
    name: 'SBAR Report',
    description: 'Structured clinical communication tool for effective handoffs',
    href: '/wizards/sbar',
    icon: FileText,
    estimatedTime: '5-10 min',
    status: 'available',
    category: 'Communication',
  },
  {
    id: 'care-plan',
    name: 'Care Planning',
    description: 'Comprehensive nursing care plan development',
    href: '/wizards/care-plan',
    icon: Heart,
    estimatedTime: '15-20 min',
    status: 'available',
    category: 'Care Management',
  },
  {
    id: 'medication',
    name: 'Medication Reconciliation',
    description: 'Verify and reconcile patient medications safely',
    href: '/wizards/medication',
    icon: Pill,
    estimatedTime: '10-15 min',
    status: 'coming-soon',
    category: 'Medication Safety',
  },
  {
    id: 'discharge',
    name: 'Discharge Planning',
    description: 'Plan safe patient discharge with comprehensive instructions',
    href: '/wizards/discharge',
    icon: Calendar,
    estimatedTime: '20-25 min',
    status: 'coming-soon',
    category: 'Transitions of Care',
  },
  {
    id: 'handoff',
    name: 'Shift Handoff',
    description: 'Structured shift-to-shift communication',
    href: '/wizards/handoff',
    icon: Users,
    estimatedTime: '5-8 min',
    status: 'coming-soon',
    category: 'Communication',
  },
  {
    id: 'education',
    name: 'Patient Education',
    description: 'Create tailored patient education materials',
    href: '/wizards/education',
    icon: BookOpen,
    estimatedTime: '10-15 min',
    status: 'coming-soon',
    category: 'Patient Engagement',
  },
]

const categories = [...new Set(wizards.map(w => w.category))]

export function WizardHub() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Clinical Wizards</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Streamline your clinical workflows with our guided wizards.
          Each tool is designed to help you create accurate, comprehensive documentation
          while following evidence-based best practices.
        </p>
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2 justify-center">
        {categories.map((category) => (
          <button
            key={category}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            {category}
          </button>
        ))}
      </div>

      {/* Wizards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {wizards.map((wizard) => (
          <div
            key={wizard.id}
            className={`group relative bg-white rounded-xl border border-gray-200 p-6 transition-all duration-200 ${
              wizard.status === 'available'
                ? 'hover:border-clinical-300 hover:shadow-lg cursor-pointer'
                : 'opacity-75'
            }`}
          >
            {/* Status Badge */}
            <div className="absolute top-4 right-4">
              {wizard.status === 'available' ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-500" />
              )}
            </div>

            {/* Icon and Category */}
            <div className="flex items-center mb-4">
              <div className="p-3 bg-clinical-100 rounded-lg">
                <wizard.icon className="w-6 h-6 text-clinical-600" />
              </div>
              <span className="ml-3 text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {wizard.category}
              </span>
            </div>

            {/* Content */}
            <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-clinical-700">
              {wizard.name}
            </h3>
            <p className="text-gray-600 mb-4 text-sm leading-relaxed">
              {wizard.description}
            </p>

            {/* Metadata */}
            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {wizard.estimatedTime}
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                wizard.status === 'available'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {wizard.status === 'available' ? 'Available' : 'Coming Soon'}
              </span>
            </div>

            {/* Action */}
            {wizard.status === 'available' ? (
              <Link
                to={wizard.href}
                className="inline-flex items-center text-clinical-600 font-medium hover:text-clinical-700 transition-colors"
              >
                Start Wizard
                <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            ) : (
              <div className="inline-flex items-center text-gray-400 font-medium">
                Coming Soon
                <Clock className="ml-2 w-4 h-4" />
              </div>
            )}

            {/* Coming Soon Overlay */}
            {wizard.status === 'coming-soon' && (
              <div className="absolute inset-0 bg-gray-50 bg-opacity-75 rounded-xl flex items-center justify-center">
                <div className="text-center">
                  <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">Coming Soon</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Help Section */}
      <div className="bg-clinical-50 rounded-xl p-6 border border-clinical-200">
        <div className="flex items-start space-x-4">
          <div className="p-2 bg-clinical-100 rounded-lg">
            <BookOpen className="w-5 h-5 text-clinical-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">New to Clinical Wizards?</h3>
            <p className="text-gray-600 mb-4">
              Our wizards are designed to guide you through complex clinical processes step-by-step.
              Each wizard includes validation, templates, and evidence-based recommendations.
            </p>
            <Link
              to="/help/wizards"
              className="inline-flex items-center text-clinical-600 font-medium hover:text-clinical-700"
            >
              Learn More About Wizards
              <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
