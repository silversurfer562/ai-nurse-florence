import { useState } from 'react';
import helpContent from '../../data/help-content.json';

interface HelpSystemProps {
  context?: string; // Optional context for contextual help
}

export function HelpSystem({ }: HelpSystemProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'tasks' | 'faq' | 'quickstart'>('quickstart');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  // Filter content based on search
  const filteredTasks = helpContent.tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredFAQs = helpContent.faqs.filter(faq =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedTaskData = helpContent.tasks.find(t => t.id === selectedTask);

  return (
    <>
      {/* Floating Help Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110 z-50"
        aria-label="Open Help"
      >
        <i className={`fas ${isOpen ? 'fa-times' : 'fa-question'} text-xl`}></i>
      </button>

      {/* Help Drawer */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
            onClick={() => setIsOpen(false)}
          ></div>

          {/* Drawer */}
          <div className="fixed right-0 top-0 h-full w-full md:w-2/3 lg:w-1/2 xl:w-2/5 bg-white shadow-2xl z-50 overflow-hidden flex flex-col">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <i className="fas fa-life-ring text-2xl"></i>
                  <h2 className="text-2xl font-bold">Help & Guide</h2>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-blue-600 rounded-full p-2 transition-colors"
                >
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>

              {/* Search */}
              <div className="relative">
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-300"></i>
                <input
                  type="text"
                  placeholder="Search for help..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200 bg-gray-50">
              <div className="flex">
                <button
                  onClick={() => { setActiveTab('quickstart'); setSearchQuery(''); }}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'quickstart'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <i className="fas fa-rocket mr-2"></i>
                  Quick Start
                </button>
                <button
                  onClick={() => { setActiveTab('tasks'); setSearchQuery(''); }}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'tasks'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <i className="fas fa-tasks mr-2"></i>
                  Tasks
                </button>
                <button
                  onClick={() => { setActiveTab('faq'); setSearchQuery(''); }}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'faq'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <i className="fas fa-question-circle mr-2"></i>
                  FAQ
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Quick Start Tab */}
              {activeTab === 'quickstart' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      {helpContent.quickStart.title}
                    </h3>
                    <p className="text-gray-600 mb-6">
                      {helpContent.quickStart.welcome}
                    </p>
                  </div>

                  {helpContent.quickStart.steps.map((step, index) => (
                    <div key={index} className="flex space-x-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1">{step.title}</h4>
                        <p className="text-gray-600 text-sm">{step.description}</p>
                      </div>
                    </div>
                  ))}

                  <div className="mt-8 bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                    <p className="text-sm text-blue-900">
                      <i className="fas fa-lightbulb mr-2"></i>
                      <strong>Tip:</strong> Click on the "Tasks" tab to see step-by-step guides for specific workflows.
                    </p>
                  </div>
                </div>
              )}

              {/* Tasks Tab */}
              {activeTab === 'tasks' && (
                <div className="space-y-4">
                  {selectedTaskData ? (
                    // Task Detail View
                    <div>
                      <button
                        onClick={() => setSelectedTask(null)}
                        className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
                      >
                        <i className="fas fa-arrow-left mr-2"></i>
                        Back to tasks
                      </button>

                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        {selectedTaskData.title}
                      </h3>
                      <p className="text-gray-600 mb-6">{selectedTaskData.description}</p>

                      {/* Steps */}
                      <div className="space-y-6 mb-8">
                        <h4 className="font-semibold text-gray-900 text-lg">Step-by-Step Guide</h4>
                        {selectedTaskData.steps.map((step) => (
                          <div key={step.step} className="border-l-4 border-blue-600 pl-4">
                            <div className="flex items-start space-x-3 mb-2">
                              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                {step.step}
                              </div>
                              <div className="flex-1">
                                <h5 className="font-semibold text-gray-900">{step.title}</h5>
                                <p className="text-gray-700 text-sm mt-1">{step.instruction}</p>
                                {step.tip && (
                                  <div className="mt-2 bg-yellow-50 border-l-2 border-yellow-400 p-2 rounded text-xs">
                                    <i className="fas fa-lightbulb text-yellow-600 mr-1"></i>
                                    <strong>Tip:</strong> {step.tip}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Benefits */}
                      <div className="mb-8">
                        <h4 className="font-semibold text-gray-900 text-lg mb-3">Benefits</h4>
                        <ul className="space-y-2">
                          {selectedTaskData.benefits.map((benefit, index) => (
                            <li key={index} className="flex items-start space-x-2 text-sm text-gray-700">
                              <i className="fas fa-check-circle text-green-600 mt-0.5"></i>
                              <span>{benefit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Troubleshooting */}
                      {selectedTaskData.troubleshooting && selectedTaskData.troubleshooting.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-900 text-lg mb-3">Troubleshooting</h4>
                          <div className="space-y-3">
                            {selectedTaskData.troubleshooting.map((item, index) => (
                              <div key={index} className="bg-gray-50 p-3 rounded">
                                <p className="font-medium text-gray-900 text-sm mb-1">
                                  <i className="fas fa-exclamation-triangle text-orange-500 mr-2"></i>
                                  {item.problem}
                                </p>
                                <p className="text-gray-700 text-sm ml-6">{item.solution}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    // Task List View
                    <>
                      {searchQuery && (
                        <p className="text-sm text-gray-600 mb-4">
                          Found {filteredTasks.length} task{filteredTasks.length !== 1 ? 's' : ''}
                        </p>
                      )}
                      {filteredTasks.map((task) => (
                        <button
                          key={task.id}
                          onClick={() => setSelectedTask(task.id)}
                          className="w-full text-left bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 mb-1">{task.title}</h4>
                              <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                              <span className="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">
                                {task.category}
                              </span>
                            </div>
                            <i className="fas fa-chevron-right text-gray-400 ml-4"></i>
                          </div>
                        </button>
                      ))}
                      {filteredTasks.length === 0 && searchQuery && (
                        <p className="text-gray-500 text-center py-8">
                          No tasks found matching "{searchQuery}"
                        </p>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* FAQ Tab */}
              {activeTab === 'faq' && (
                <div className="space-y-4">
                  {searchQuery && (
                    <p className="text-sm text-gray-600 mb-4">
                      Found {filteredFAQs.length} question{filteredFAQs.length !== 1 ? 's' : ''}
                    </p>
                  )}
                  {filteredFAQs.map((faq) => (
                    <details key={faq.id} className="bg-white border border-gray-200 rounded-lg group">
                      <summary className="cursor-pointer p-4 hover:bg-gray-50 transition-colors flex items-start justify-between">
                        <div className="flex-1 pr-4">
                          <h4 className="font-semibold text-gray-900 mb-1">{faq.question}</h4>
                          <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                            {faq.category}
                          </span>
                        </div>
                        <i className="fas fa-chevron-down text-gray-400 group-open:rotate-180 transition-transform"></i>
                      </summary>
                      <div className="px-4 pb-4 text-sm text-gray-700 border-t border-gray-100 pt-3">
                        {faq.answer}
                      </div>
                    </details>
                  ))}
                  {filteredFAQs.length === 0 && searchQuery && (
                    <p className="text-gray-500 text-center py-8">
                      No FAQs found matching "{searchQuery}"
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
              <p>
                Need more help?{' '}
                <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                  Contact Support
                </a>
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default HelpSystem;
