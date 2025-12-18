import React from 'react';
import { useAppContext } from '@/contexts/AppContext';
import { useIsMobile } from '@/hooks/use-mobile';
import { BookOpen, Users, FileText, Award, Plus, LogIn, Code, CheckCircle, Clock, GraduationCap, Shield, Database, Layers, ArrowRight, Github, ExternalLink, Mail, Bell, Send, Inbox } from 'lucide-react';

const AppLayout: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useAppContext();
  const isMobile = useIsMobile();

  const features = [
    {
      icon: Shield,
      title: 'Role-Based Access Control',
      description: 'Dual-layer permission enforcement at both view and queryset levels. Teachers and students have distinct capabilities.',
      color: 'from-blue-500 to-indigo-600'
    },
    {
      icon: Layers,
      title: 'Class-Based Views Only',
      description: 'ListView, CreateView, UpdateView, DetailView, DeleteView, and FormView with custom permission mixins.',
      color: 'from-purple-500 to-pink-600'
    },
    {
      icon: Database,
      title: 'Clean Model Architecture',
      description: 'TeacherProfile, Classroom, ClassroomMembership, and ProjectSubmission with proper relationships.',
      color: 'from-emerald-500 to-teal-600'
    },
    {
      icon: FileText,
      title: 'Django Forms & ModelForms',
      description: 'Comprehensive form validation for registration, classroom management, submissions, and grading.',
      color: 'from-orange-500 to-red-600'
    },
    {
      icon: CheckCircle,
      title: 'Filtering & Pagination',
      description: 'Combinable filters for status, grade range, classroom, and student with paginated results.',
      color: 'from-cyan-500 to-blue-600'
    },
    {
      icon: Mail,
      title: 'Email Notifications',
      description: 'Automated emails for submissions, grading, and classroom joins with beautiful HTML templates.',
      color: 'from-rose-500 to-pink-600'
    }
  ];

  const models = [
    {
      name: 'TeacherProfile',
      description: 'One-to-one extension of User to mark teachers',
      fields: ['user (OneToOne)', 'department', 'created_at']
    },
    {
      name: 'Classroom',
      description: 'Represents one project assignment tied to a teacher',
      fields: ['title', 'description', 'requirements_file', 'join_code (unique)', 'teacher (FK)', 'is_active', 'created_at']
    },
    {
      name: 'ClassroomMembership',
      description: 'Links students to classrooms with metadata',
      fields: ['classroom (FK)', 'student (FK)', 'joined_at']
    },
    {
      name: 'ProjectSubmission',
      description: 'Student project work with grading workflow',
      fields: ['classroom (FK)', 'title', 'description', 'repository_url', 'deployed_url', 'collaborators (M2M)', 'status', 'grade (1-20)', 'teacher_notes', 'created_by (FK)']
    }
  ];

  const views = [
    { name: 'DashboardView', type: 'TemplateView', access: 'All', description: 'Role-based dashboard' },
    { name: 'ClassroomListView', type: 'ListView', access: 'All', description: 'List classrooms (filtered by role)' },
    { name: 'ClassroomCreateView', type: 'CreateView', access: 'Teachers', description: 'Create new classroom' },
    { name: 'JoinClassroomView', type: 'FormView', access: 'Students', description: 'Join via code' },
    { name: 'SubmissionCreateView', type: 'CreateView', access: 'Members', description: 'Create project submission' },
    { name: 'SubmissionUpdateView', type: 'UpdateView', access: 'Creator (Draft)', description: 'Edit submission' },
    { name: 'GradeSubmissionView', type: 'UpdateView', access: 'Teachers', description: 'Grade a submission' },
    { name: 'MyGradesView', type: 'ListView', access: 'Students', description: 'View all grades' },
  ];

  const files = [
    { name: 'models.py', lines: '~250', description: 'Data models with validation and helper functions' },
    { name: 'forms.py', lines: '~350', description: 'ModelForms and custom forms with validation' },
    { name: 'views.py', lines: '~600', description: '20+ Class-Based Views with permission mixins' },
    { name: 'urls.py', lines: '~100', description: 'RESTful URL configuration' },
    { name: 'notifications.py', lines: '~250', description: 'Email notification functions' },
    { name: 'signals.py', lines: '~150', description: 'Django signals for email triggers' },
    { name: 'admin.py', lines: '~150', description: 'Django admin with inlines and custom displays' },
    { name: 'mixins.py', lines: '~200', description: 'Reusable permission mixins' },
    { name: 'tests.py', lines: '~450', description: 'Comprehensive test suite' },
    { name: 'README.md', lines: '~400', description: 'Complete documentation' },
  ];

  const emailNotifications = [
    {
      trigger: 'Project Submission',
      recipient: 'Teacher',
      description: 'When a student submits their project, the teacher receives an email with project details, repository URL, and collaborator list.',
      icon: Send,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      trigger: 'Grade Assignment',
      recipient: 'Student + Collaborators',
      description: 'When a teacher grades a project, all participants receive an email with their grade, percentage, and teacher feedback.',
      icon: Award,
      color: 'from-emerald-500 to-green-500'
    },
    {
      trigger: 'Classroom Join',
      recipient: 'Student',
      description: 'When a student joins a classroom, they receive a welcome email with classroom details, teacher info, and next steps.',
      icon: Inbox,
      color: 'from-purple-500 to-pink-500'
    }
  ];

  const emailTemplates = [
    { name: 'base_email.html', description: 'Base template with common styles, header, and footer' },
    { name: 'submission_notification.html', description: 'Teacher notification for new submissions' },
    { name: 'grade_notification.html', description: 'Student notification with grade and feedback' },
    { name: 'welcome_email.html', description: 'Welcome email for classroom joins' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20" />
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm mb-6">
              <GraduationCap className="w-4 h-4" />
              Django Backend Project
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
              University Project
              <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Submission Platform
              </span>
            </h1>
            
            <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
              A comprehensive Django backend demonstrating Authentication, Forms, CRUD operations, 
              Filtering, Class-Based Views, and Email Notifications with clean RBAC architecture.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4">
              <a 
                href="#models" 
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
              >
                View Architecture
                <ArrowRight className="w-4 h-4" />
              </a>
              <a 
                href="#emails" 
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors"
              >
                <Mail className="w-4 h-4" />
                Email System
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Features Grid */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Core Features</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Built to demonstrate mastery of Django fundamentals with clean, production-ready code
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group p-6 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-slate-600 transition-all duration-300"
              >
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} mb-4`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Email Notifications Section */}
      <section id="emails" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-rose-500/5 to-purple-500/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-rose-500/10 border border-rose-500/20 rounded-full text-rose-400 text-sm mb-4">
              <Bell className="w-4 h-4" />
              New Feature
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">Email Notifications</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Automated email notifications keep teachers and students informed at every step
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {emailNotifications.map((notification, index) => (
              <div 
                key={index}
                className="p-6 bg-slate-800/80 border border-slate-700 rounded-xl hover:border-rose-500/30 transition-all duration-300"
              >
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${notification.color} mb-4`}>
                  <notification.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{notification.trigger}</h3>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded">
                    To: {notification.recipient}
                  </span>
                </div>
                <p className="text-slate-400 text-sm">{notification.description}</p>
              </div>
            ))}
          </div>

          {/* Email Templates */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-rose-400" />
              HTML Email Templates
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {emailTemplates.map((template, index) => (
                <div 
                  key={index}
                  className="p-4 bg-slate-900/50 border border-slate-700 rounded-lg"
                >
                  <code className="text-rose-400 text-sm">{template.name}</code>
                  <p className="text-slate-500 text-xs mt-1">{template.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Email Configuration */}
          <div className="mt-8 grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Supported Backends</h3>
              <ul className="space-y-2">
                {['Console (Development)', 'SMTP (Production)', 'Gmail SMTP', 'SendGrid', 'Amazon SES'].map((backend, i) => (
                  <li key={i} className="flex items-center gap-2 text-slate-300">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    {backend}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Signal-Based Triggers</h3>
              <p className="text-slate-400 text-sm mb-4">
                Emails are triggered automatically via Django signals when:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-slate-300">
                  <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                  Submission status changes to SUBMITTED
                </li>
                <li className="flex items-center gap-2 text-slate-300">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full"></span>
                  Grade is assigned to a submission
                </li>
                <li className="flex items-center gap-2 text-slate-300">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  ClassroomMembership is created
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Models Section */}
      <section id="models" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Data Models</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Clean model relationships with proper Django conventions
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {models.map((model, index) => (
              <div 
                key={index}
                className="p-6 bg-slate-800 border border-slate-700 rounded-xl"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-emerald-500/10 rounded-lg">
                    <Database className="w-5 h-5 text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">{model.name}</h3>
                </div>
                <p className="text-slate-400 mb-4">{model.description}</p>
                <div className="flex flex-wrap gap-2">
                  {model.fields.map((field, i) => (
                    <span 
                      key={i}
                      className="px-3 py-1 bg-slate-700 text-slate-300 text-sm rounded-full"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Views Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Class-Based Views</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              20+ CBVs with custom permission mixins for role-based access control
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-slate-400 font-medium">View</th>
                  <th className="text-left py-4 px-4 text-slate-400 font-medium">Type</th>
                  <th className="text-left py-4 px-4 text-slate-400 font-medium">Access</th>
                  <th className="text-left py-4 px-4 text-slate-400 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {views.map((view, index) => (
                  <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                    <td className="py-4 px-4">
                      <code className="text-blue-400">{view.name}</code>
                    </td>
                    <td className="py-4 px-4">
                      <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-sm rounded">
                        {view.type}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-sm rounded">
                        {view.access}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-slate-300">{view.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Files Section */}
      <section id="files" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Project Files</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Complete Django application with comprehensive documentation
            </p>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {files.map((file, index) => (
              <div 
                key={index}
                className="p-4 bg-slate-800 border border-slate-700 rounded-lg hover:border-blue-500/50 transition-colors group"
              >
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <code className="text-white font-medium">{file.name}</code>
                </div>
                <p className="text-slate-400 text-sm mb-2">{file.description}</p>
                <span className="text-xs text-slate-500">{file.lines} lines</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">User Workflows</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Clear separation between student and teacher capabilities with email notifications
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Student Flow */}
            <div className="p-6 bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Users className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-2xl font-bold text-white">Student Flow</h3>
              </div>
              <ul className="space-y-4">
                {[
                  { step: 'Register / Login', email: false },
                  { step: 'Join classroom using join code', email: true, emailNote: 'Welcome email sent' },
                  { step: 'Create project submission', email: false },
                  { step: 'Select collaborators from classroom members', email: false },
                  { step: 'Submit project (becomes read-only)', email: true, emailNote: 'Teacher notified' },
                  { step: 'View grades when assigned', email: true, emailNote: 'Grade email received' }
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-sm font-medium">
                      {i + 1}
                    </span>
                    <div>
                      <span className="text-slate-300">{item.step}</span>
                      {item.email && (
                        <span className="ml-2 inline-flex items-center gap-1 text-xs text-rose-400">
                          <Mail className="w-3 h-3" />
                          {item.emailNote}
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Teacher Flow */}
            <div className="p-6 bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <GraduationCap className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-2xl font-bold text-white">Teacher Flow</h3>
              </div>
              <ul className="space-y-4">
                {[
                  { step: 'Register as teacher / Login', email: false },
                  { step: 'Create classrooms with unique join codes', email: false },
                  { step: 'Upload project requirements', email: false },
                  { step: 'View submitted projects per classroom', email: true, emailNote: 'Notified on submissions' },
                  { step: 'Assign grades (1-20) and notes', email: true, emailNote: 'Students notified' },
                  { step: 'Export grades to CSV', email: false }
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-purple-500/20 text-purple-400 rounded-full flex items-center justify-center text-sm font-medium">
                      {i + 1}
                    </span>
                    <div>
                      <span className="text-slate-300">{item.step}</span>
                      {item.email && (
                        <span className="ml-2 inline-flex items-center gap-1 text-xs text-rose-400">
                          <Mail className="w-3 h-3" />
                          {item.emailNote}
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Permission Matrix */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Permission Matrix</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Comprehensive RBAC enforced at view and queryset levels
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-slate-400 font-medium">Action</th>
                  <th className="text-center py-4 px-4 text-slate-400 font-medium">Student</th>
                  <th className="text-center py-4 px-4 text-slate-400 font-medium">Teacher</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { action: 'Create Classroom', student: false, teacher: true },
                  { action: 'Join Classroom', student: true, teacher: false },
                  { action: 'Create Submission', student: true, teacher: false, note: '(member)' },
                  { action: 'Edit Submission', student: true, teacher: false, note: '(creator, draft)' },
                  { action: 'View Submission', student: true, teacher: true, note: '(participant/owner)' },
                  { action: 'Grade Submission', student: false, teacher: true },
                  { action: 'View Grades', student: true, teacher: true, note: '(own/all)' },
                ].map((row, index) => (
                  <tr key={index} className="border-b border-slate-700/50">
                    <td className="py-4 px-4 text-slate-300">
                      {row.action}
                      {row.note && <span className="text-slate-500 text-sm ml-1">{row.note}</span>}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {row.student ? (
                        <CheckCircle className="w-5 h-5 text-emerald-400 mx-auto" />
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {row.teacher ? (
                        <CheckCircle className="w-5 h-5 text-emerald-400 mx-auto" />
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-slate-800">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">University Project Submission Platform</h3>
                <p className="text-slate-400 text-sm">Django Backend Project with Email Notifications</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6 text-slate-400 text-sm">
              <span>Django 4.x</span>
              <span>Python 3.x</span>
              <span>CBVs</span>
              <span>RBAC</span>
              <span className="text-rose-400">Email</span>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
            Built for university evaluation demonstrating Django fundamentals, clean backend architecture, and email notifications
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;
