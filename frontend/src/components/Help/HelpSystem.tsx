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
      {/* Hidden trigger button for header help button to click */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="help-system-button hidden"
        aria-label="Toggle Help"
      />

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
                  aria-label="Close Help"
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
                    <h3 className="text-xl font-bold text-gray-800 mb-3">{helpContent.quickStart.title}</h3>
                    <p className="text-gray-600 mb-4">{helpContent.quickStart.welcome}</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-800 mb-3">Getting Started</h4>
                    <div className="space-y-3">
                      {helpContent.quickStart.steps.map((step: any, index: number) => (
                        <div key={index} className="flex gap-3">
                          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                            {index + 1}
                          </div>
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-800">{step.title}</h5>
                            <p className="text-sm text-gray-600">{step.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Tasks Tab */}
              {activeTab === 'tasks' && (
                <div className="space-y-4">
                  {selectedTask ? (
                    // Task Details View
                    <div>
                      <button
                        onClick={() => setSelectedTask(null)}
                        className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
                      >
                        <i className="fas fa-arrow-left"></i>
                        Back to all tasks
                      </button>

                      {selectedTaskData && (
                        <div className="space-y-6">
                          <div>
                            <h3 className="text-2xl font-bold text-gray-800 mb-2">{selectedTaskData.title}</h3>
                            <p className="text-gray-600">{selectedTaskData.description}</p>
                          </div>

                          <div>
                            <h4 className="font-semibold text-gray-800 mb-3">Steps</h4>
                            <div className="space-y-3">
                              {selectedTaskData.steps.map((step: any, index: number) => (
                                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                                  <div className="flex items-start gap-3">
                                    <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                                      {index + 1}
                                    </div>
                                    <div className="flex-1">
                                      <h5 className="font-medium text-gray-800 mb-1">{step.title}</h5>
                                      <p className="text-sm text-gray-600 mb-2">{step.instruction}</p>
                                      {step.tip && (
                                        <div className="bg-blue-50 border-l-2 border-blue-400 pl-3 py-1 text-sm text-blue-800">
                                          <i className="fas fa-lightbulb mr-1"></i>
                                          <strong>Tip:</strong> {step.tip}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {selectedTaskData.benefits && (
                            <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded-r">
                              <h4 className="font-semibold text-green-900 mb-2">
                                <i className="fas fa-check-circle mr-2"></i>
                                Benefits
                              </h4>
                              <ul className="space-y-1 text-sm text-green-800">
                                {selectedTaskData.benefits.map((benefit: string, index: number) => (
                                  <li key={index}>• {benefit}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {selectedTaskData.troubleshooting && (
                            <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4 rounded-r">
                              <h4 className="font-semibold text-yellow-900 mb-2">
                                <i className="fas fa-wrench mr-2"></i>
                                Troubleshooting
                              </h4>
                              <ul className="space-y-1 text-sm text-yellow-800">
                                {selectedTaskData.troubleshooting.map((item: any, index: number) => (
                                  <li key={index}>• {typeof item === 'string' ? item : `${item.problem}: ${item.solution}`}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    // Task List View
                    <>
                      <h3 className="text-xl font-bold text-gray-800 mb-4">How-To Guides</h3>
                      {filteredTasks.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No tasks match your search.</p>
                      ) : (
                        <div className="space-y-3">
                          {filteredTasks.map((task) => (
                            <button
                              key={task.id}
                              onClick={() => setSelectedTask(task.id)}
                              className="w-full text-left bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all group"
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <h4 className="font-semibold text-gray-800 group-hover:text-blue-600 mb-1">
                                    {task.title}
                                  </h4>
                                  <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                                  <span className="inline-block text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                    {task.category}
                                  </span>
                                </div>
                                <i className="fas fa-chevron-right text-gray-400 group-hover:text-blue-600 mt-1"></i>
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* FAQ Tab */}
              {activeTab === 'faq' && (
                <div className="space-y-4">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">Frequently Asked Questions</h3>
                  {filteredFAQs.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No FAQs match your search.</p>
                  ) : (
                    <div className="space-y-3">
                      {filteredFAQs.map((faq, index) => (
                        <details
                          key={index}
                          className="bg-white border border-gray-200 rounded-lg overflow-hidden group"
                        >
                          <summary className="px-4 py-3 cursor-pointer hover:bg-gray-50 flex items-start justify-between group">
                            <span className="font-medium text-gray-800 pr-4">{faq.question}</span>
                            <i className="fas fa-chevron-down text-gray-400 group-hover:text-blue-600 mt-1"></i>
                          </summary>
                          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                            <p className="text-sm text-gray-700">{faq.answer}</p>
                            {(faq as any).related_tasks && (faq as any).related_tasks.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-gray-200">
                                <p className="text-xs text-gray-600 mb-2">Related guides:</p>
                                <div className="flex flex-wrap gap-2">
                                  {(faq as any).related_tasks.map((taskId: string, i: number) => {
                                    const task = helpContent.tasks.find(t => t.id === taskId);
                                    return task ? (
                                      <button
                                        key={i}
                                        onClick={() => {
                                          setActiveTab('tasks');
                                          setSelectedTask(taskId);
                                        }}
                                        className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                                      >
                                        {task.title}
                                      </button>
                                    ) : null;
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                        </details>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}
