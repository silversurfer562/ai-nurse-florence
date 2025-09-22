/**
 * AI Nurse Florence - Professional Clinical Workspace
 * Continuing Education & Clinical Documentation Assistant
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Stethoscope, 
  FileText, 
  GraduationCap, 
  Users, 
  ClipboardList,
  MessageSquare,
  HeartPulse,
  BookOpen
} from 'lucide-react';

interface ClinicalWorkspaceProps {
  nurseProfile?: {
    name: string;
    unit: string;
    experience: string;
    specialties: string[];
  };
}

export default function ClinicalWorkspace({ nurseProfile }: ClinicalWorkspaceProps) {
  const [activeWorkflow, setActiveWorkflow] = useState<string>('dashboard');

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Professional Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Stethoscope className="h-8 w-8 text-blue-600" />
                <span className="text-xl font-semibold text-slate-900">
                  AI Nurse Florence
                </span>
              </div>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                Continuing Education Assistant
              </Badge>
            </div>
            
            {nurseProfile && (
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900">{nurseProfile.name}</p>
                  <p className="text-xs text-slate-500">{nurseProfile.unit} • {nurseProfile.experience}</p>
                </div>
                <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">
                    {nurseProfile.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Tabs value={activeWorkflow} onValueChange={setActiveWorkflow} className="space-y-6">
          {/* Navigation Tabs */}
          <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8 gap-2 h-auto p-2 bg-white rounded-lg border">
            <TabsTrigger value="dashboard" className="flex flex-col items-center space-y-1 h-16">
              <HeartPulse className="h-5 w-5" />
              <span className="text-xs">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="continuing-ed" className="flex flex-col items-center space-y-1 h-16">
              <GraduationCap className="h-5 w-5" />
              <span className="text-xs">Learning</span>
            </TabsTrigger>
            <TabsTrigger value="documentation" className="flex flex-col items-center space-y-1 h-16">
              <FileText className="h-5 w-5" />
              <span className="text-xs">Documents</span>
            </TabsTrigger>
            <TabsTrigger value="communication" className="flex flex-col items-center space-y-1 h-16">
              <MessageSquare className="h-5 w-5" />
              <span className="text-xs">Communication</span>
            </TabsTrigger>
            <TabsTrigger value="patient-ed" className="flex flex-col items-center space-y-1 h-16">
              <BookOpen className="h-5 w-5" />
              <span className="text-xs">Patient Ed</span>
            </TabsTrigger>
            <TabsTrigger value="assessments" className="flex flex-col items-center space-y-1 h-16">
              <ClipboardList className="h-5 w-5" />
              <span className="text-xs">Assessments</span>
            </TabsTrigger>
            <TabsTrigger value="collaboration" className="flex flex-col items-center space-y-1 h-16">
              <Users className="h-5 w-5" />
              <span className="text-xs">Team</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <QuickActionCard 
                icon={<GraduationCap className="h-6 w-6" />}
                title="Today's Learning"
                description="3 new CEU modules available"
                action="Start Learning"
                className="bg-blue-50 border-blue-200 hover:bg-blue-100"
              />
              <QuickActionCard 
                icon={<FileText className="h-6 w-6" />}
                title="Draft Documents"
                description="2 SBAR reports, 1 care plan"
                action="Review Drafts"
                className="bg-green-50 border-green-200 hover:bg-green-100"
              />
              <QuickActionCard 
                icon={<MessageSquare className="h-6 w-6" />}
                title="Team Messages"
                description="Physician consultation ready"
                action="View Messages"
                className="bg-purple-50 border-purple-200 hover:bg-purple-100"
              />
              <QuickActionCard 
                icon={<ClipboardList className="h-6 w-6" />}
                title="Clinical Tools"
                description="Vital signs, medications, assessments"
                action="Open Tools"
                className="bg-orange-50 border-orange-200 hover:bg-orange-100"
              />
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <HeartPulse className="h-5 w-5 text-blue-600" />
                  <span>Recent Activity</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <ActivityItem 
                    time="2 minutes ago"
                    action="Generated SBAR report"
                    detail="Patient: J.D. - Post-op wound assessment"
                    status="draft"
                  />
                  <ActivityItem 
                    time="15 minutes ago"
                    action="Completed CEU module"
                    detail="Cardiac Rhythm Interpretation - Advanced"
                    status="completed"
                  />
                  <ActivityItem 
                    time="1 hour ago"
                    action="Created patient education"
                    detail="Diabetes management handout for Mrs. Chen"
                    status="sent"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Continuing Education */}
          <TabsContent value="continuing-ed" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Work-Related Q&A</CardTitle>
                  <p className="text-sm text-slate-600">
                    Get evidence-based answers to clinical questions as they arise
                  </p>
                </CardHeader>
                <CardContent>
                  <ContinuingEducationInterface type="qa" />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Clinical Scenarios</CardTitle>
                  <p className="text-sm text-slate-600">
                    Interactive case studies for decision-making practice
                  </p>
                </CardHeader>
                <CardContent>
                  <ContinuingEducationInterface type="scenarios" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Documentation */}
          <TabsContent value="documentation" className="space-y-6">
            <DocumentationWorkspace />
          </TabsContent>

          {/* Other tabs would be implemented similarly */}
        </Tabs>
      </main>
    </div>
  );
}

// Quick Action Card Component
function QuickActionCard({ 
  icon, 
  title, 
  description, 
  action, 
  className = "" 
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  action: string;
  className?: string;
}) {
  return (
    <Card className={`transition-colors cursor-pointer ${className}`}>
      <CardContent className="p-6">
        <div className="flex items-center space-x-3 mb-3">
          {icon}
          <h3 className="font-medium text-slate-900">{title}</h3>
        </div>
        <p className="text-sm text-slate-600 mb-4">{description}</p>
        <Button size="sm" variant="outline" className="w-full">
          {action}
        </Button>
      </CardContent>
    </Card>
  );
}

// Activity Item Component
function ActivityItem({ 
  time, 
  action, 
  detail, 
  status 
}: {
  time: string;
  action: string;
  detail: string;
  status: 'draft' | 'completed' | 'sent';
}) {
  const statusColors = {
    draft: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    completed: 'bg-green-100 text-green-800 border-green-200',
    sent: 'bg-blue-100 text-blue-800 border-blue-200'
  };

  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
      <div className="flex-1">
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-900">{action}</p>
            <p className="text-xs text-slate-500">{detail}</p>
          </div>
          <Badge className={statusColors[status]}>{status}</Badge>
        </div>
        <p className="text-xs text-slate-400 mt-1">{time}</p>
      </div>
    </div>
  );
}

// Continuing Education Interface
function ContinuingEducationInterface({ type }: { type: 'qa' | 'scenarios' }) {
  if (type === 'qa') {
    return (
      <div className="space-y-4">
        <div className="bg-slate-50 rounded-lg p-4">
          <h4 className="font-medium text-slate-900 mb-2">Ask a Clinical Question</h4>
          <textarea 
            className="w-full p-3 border border-slate-200 rounded-md resize-none"
            rows={3}
            placeholder="e.g., What are the early signs of sepsis in elderly patients?"
          />
          <Button className="mt-2" size="sm">Get Evidence-Based Answer</Button>
        </div>
        
        <div className="space-y-2">
          <h5 className="text-sm font-medium text-slate-700">Popular Questions Today</h5>
          <div className="space-y-1">
            <button className="text-left w-full p-2 text-sm text-slate-600 hover:bg-slate-50 rounded">
              • Medication calculations for pediatric patients
            </button>
            <button className="text-left w-full p-2 text-sm text-slate-600 hover:bg-slate-50 rounded">
              • Post-surgical wound care protocols
            </button>
            <button className="text-left w-full p-2 text-sm text-slate-600 hover:bg-slate-50 rounded">
              • Diabetic ketoacidosis management
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-slate-50 rounded-lg p-4">
        <h4 className="font-medium text-slate-900 mb-2">Current Scenario</h4>
        <p className="text-sm text-slate-600 mb-3">
          You're caring for a 68-year-old patient with CHF. Their BP is 160/95, HR 110, 
          and they're showing signs of fluid overload...
        </p>
        <Button size="sm">Continue Scenario</Button>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        <Button variant="outline" size="sm">New Scenario</Button>
        <Button variant="outline" size="sm">Review Completed</Button>
      </div>
    </div>
  );
}

// Documentation Workspace
function DocumentationWorkspace() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>SBAR Reports</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <span>+ New SBAR Report</span>
            </Button>
            <div className="space-y-2">
              <div className="p-2 border border-slate-200 rounded text-sm">
                <strong>Patient J.D.</strong> - Post-op assessment
                <Badge className="ml-2 bg-yellow-100 text-yellow-800">Draft</Badge>
              </div>
              <div className="p-2 border border-slate-200 rounded text-sm">
                <strong>Patient M.K.</strong> - Medication concern
                <Badge className="ml-2 bg-green-100 text-green-800">Sent</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Allied Health Communication</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <span>+ Draft Email to Physician</span>
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <span>+ Physical Therapy Referral</span>
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <span>+ Social Work Consultation</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BookOpen className="h-5 w-5" />
            <span>Patient Education Materials</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <span>+ Create Patient Handout</span>
            </Button>
            <div className="space-y-2">
              <div className="p-2 border border-slate-200 rounded text-sm">
                <strong>Diabetes Management</strong>
                <Badge className="ml-2 bg-blue-100 text-blue-800">Ready</Badge>
              </div>
              <div className="p-2 border border-slate-200 rounded text-sm">
                <strong>Post-Op Care Instructions</strong>
                <Badge className="ml-2 bg-yellow-100 text-yellow-800">Draft</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
