import { Activity, ArrowRight, BookOpen, FileText, Stethoscope } from 'lucide-react'
import { Link } from 'react-router-dom'

const quickActions = [
  {
    name: 'SBAR Report',
    description: 'Create structured clinical communication',
    href: '/wizards/sbar',
    icon: FileText,
    color: 'bg-blue-500',
  },
  {
    name: 'Care Planning',
    description: 'Develop comprehensive care plans',
    href: '/wizards/care-plan',
    icon: Stethoscope,
    color: 'bg-green-500',
  },
  {
    name: 'Patient Education',
    description: 'Create educational materials',
    href: '/wizards/education',
    icon: BookOpen,
    color: 'bg-purple-500',
  },
  {
    name: 'Clinical Analytics',
    description: 'Review workflow metrics',
    href: '/analytics',
    icon: Activity,
    color: 'bg-orange-500',
  },
]

const recentActivity = [
  {
    type: 'SBAR Report',
    patient: 'Room 302A',
    time: '15 minutes ago',
    status: 'completed',
  },
  {
    type: 'Care Plan',
    patient: 'Room 418B',
    time: '1 hour ago',
    status: 'in-progress',
  },
  {
    type: 'Medication Review',
    patient: 'Room 205C',
    time: '2 hours ago',
    status: 'completed',
  },
]

export function HomePage() {
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-clinical-600 to-clinical-700 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to AI Nurse Florence</h1>
        <p className="text-clinical-100 text-lg">
          Your intelligent healthcare assistant for clinical documentation and decision support.
        </p>
        <div className="mt-6 flex items-center gap-4">
          <Link
            to="/wizards"
            className="inline-flex items-center px-6 py-3 bg-white text-clinical-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
            Start Clinical Wizard
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
          <Link
            to="/clinical"
            className="inline-flex items-center px-6 py-3 border border-clinical-200 text-white rounded-lg font-semibold hover:bg-clinical-600 transition-colors"
          >
            Browse Tools
          </Link>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action) => (
            <Link
              key={action.name}
              to={action.href}
              className="group p-6 bg-white rounded-xl border border-gray-200 hover:border-clinical-300 hover:shadow-lg transition-all duration-200"
            >
              <div className="flex items-center mb-4">
                <div className={`p-3 rounded-lg ${action.color} text-white`}>
                  <action.icon className="w-6 h-6" />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-clinical-700">
                {action.name}
              </h3>
              <p className="text-sm text-gray-600">
                {action.description}
              </p>
              <div className="mt-4 flex items-center text-clinical-600 text-sm font-medium">
                Start now
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Activity</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg font-semibold text-gray-900">Your Clinical Workflow</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {recentActivity.map((activity, index) => (
              <div key={index} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${
                      activity.status === 'completed'
                        ? 'bg-green-500'
                        : activity.status === 'in-progress'
                        ? 'bg-yellow-500'
                        : 'bg-gray-400'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {activity.type} - {activity.patient}
                      </p>
                      <p className="text-sm text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    activity.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : activity.status === 'in-progress'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {activity.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
