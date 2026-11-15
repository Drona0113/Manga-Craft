import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Bot, Image, Palette, Brain, MessageSquare, Sparkles, Play } from 'lucide-react';
import api from '../services/api';

function Home() {
  const [showTutorial, setShowTutorial] = useState(false);
  const [dismissedTutorial, setDismissedTutorial] = useState(false);

  useEffect(() => {
    const tutorialDismissed = localStorage.getItem('tutorialDismissed');
    if (!tutorialDismissed) {
      setShowTutorial(true);
    }
  }, []);

  const handleDismissTutorial = () => {
    setShowTutorial(false);
    setDismissedTutorial(true);
    localStorage.setItem('tutorialDismissed', 'true');
  };

  const handleShowTutorial = () => {
    setShowTutorial(true);
  };

  const features = [
    {
      icon: BookOpen,
      title: 'Project Management',
      description: 'Organize your manga projects with dedicated workspaces. Keep your stories, characters, and creative work structured and accessible.'
    },
    {
      icon: Bot,
      title: 'AI Assistance',
      description: 'Interact with AI that understands your project context. Get creative suggestions, brainstorm ideas, and solve storytelling challenges.'
    },
    {
      icon: Image,
      title: 'Panel Analysis',
      description: 'Upload manga panels for AI-powered analysis. Understand composition, visual flow, and get actionable feedback for improvement.'
    },
    {
      icon: Palette,
      title: 'Reference Generation',
      description: 'Generate AI-created reference images for your panels. Visualize your scenes before drawing, saving time and ensuring consistency.'
    },
    {
      icon: Brain,
      title: 'Project Memory',
      description: 'Store characters, story details, and relationships as persistent memory. The AI recalls this context during conversations.'
    },
    {
      icon: MessageSquare,
      title: 'Conversation History',
      description: 'Maintain chat history within each project. Review past discussions, track decisions, and maintain continuity in your creative process.'
    },
  ];

  const benefits = [
    {
      title: 'Built for Manga Creators',
      description: 'Unlike generic AI tools, MangaCraft is designed specifically for manga creation. It understands panel composition, character relationships, and storytelling conventions unique to manga.'
    },
    {
      title: 'Context-Aware Intelligence',
      description: 'The AI remembers your project\'s characters, story details, and creative decisions. No need to repeat context every conversation—MangaCraft keeps track for you.'
    },
    {
      title: 'Everything in One Place',
      description: 'Projects, panels, references, conversations, and memory—all organized in one workspace. Switch between tools without losing your creative flow.'
    },
    {
      title: 'Iterative Creative Process',
      description: 'Upload panels, get AI feedback, generate references, and refine your work. MangaCraft supports your entire creative workflow from idea to completion.'
    },
  ];

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center py-16 lg:py-24"
      >
        <h1 className="text-5xl lg:text-6xl font-bold text-[var(--text-primary)] mb-4">MangaCraft</h1>
        <p className="text-xl lg:text-2xl text-[var(--text-secondary)] mb-6">AI-Powered Manga Creation Workspace</p>
        <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto leading-relaxed">
          Bring your manga stories to life with intelligent assistance. Manage projects, analyze panels, 
          generate references, and maintain creative context—all in one dedicated workspace.
        </p>
        <div className="flex justify-center gap-4 mt-8">
          <Link to="/projects" className="bg-[var(--accent)] text-white px-8 py-3 rounded-lg hover:opacity-90 transition font-medium">
            <Sparkles className="inline w-5 h-5 mr-2" />
            Start Creating
          </Link>
          <button
            onClick={handleShowTutorial}
            className="bg-[var(--bg-card)] text-[var(--text-primary)] px-8 py-3 rounded-lg border border-[var(--border)] hover:bg-[var(--border)] transition font-medium"
          >
            Learn More
          </button>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="max-w-6xl mx-auto py-16"
      >
        <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-12 text-center">What MangaCraft Offers</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="mb-4 flex justify-center">
                <feature.icon className="w-12 h-12 text-[var(--accent)]" />
              </div>
              <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">{feature.title}</h3>
              <p className="text-[var(--text-secondary)]">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="bg-[var(--bg-surface)] border-t border-[var(--border)] py-16"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-6 text-center">Why MangaCraft?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {benefits.map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-3">{benefit.title}</h3>
                <p className="text-[var(--text-secondary)] leading-relaxed">
                  {benefit.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center py-16"
      >
        <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-4">Ready to Create?</h2>
        <p className="text-[var(--text-secondary)] mb-8 max-w-xl mx-auto">
          Start your first manga project and experience the future of AI-assisted manga creation.
        </p>
        <Link to="/projects" className="inline-flex items-center bg-[var(--accent)] text-white px-8 py-3 rounded-lg hover:opacity-90 transition font-medium">
          <Play className="w-5 h-5 mr-2" />
          Create Your First Project
        </Link>
      </motion.div>

      {showTutorial && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={handleDismissTutorial} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
            className="relative bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-[var(--text-primary)]">Welcome to MangaCraft</h3>
              <button
                onClick={handleDismissTutorial}
                className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-2xl"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6 text-left">
              <div>
                <h4 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Getting Started</h4>
                <p className="text-[var(--text-secondary)] mb-4">
                  MangaCraft is your AI-powered manga creation workspace. Here's how to use it:
                </p>
                
                <div className="space-y-4">
                  <div className="border-l-2 border-[var(--accent)] pl-4">
                    <h5 className="font-semibold text-[var(--text-primary)]">Projects</h5>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Create and manage your manga projects. Each project contains your story, characters, panels, and creative work.
                    </p>
                  </div>
                  
                  <div className="border-l-2 border-[var(--accent)] pl-4">
                    <h5 className="font-semibold text-[var(--text-primary)]">AI Chat</h5>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Chat with AI to get creative assistance, brainstorm ideas, and get help with your manga. The AI remembers your project context.
                    </p>
                  </div>
                  
                  <div className="border-l-2 border-[var(--accent)] pl-4">
                    <h5 className="font-semibold text-[var(--text-primary)]">Panels</h5>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Upload manga panels for AI analysis. Get composition insights, visual suggestions, and reference generation.
                    </p>
                  </div>
                  
                  <div className="border-l-2 border-[var(--accent)] pl-4">
                    <h5 className="font-semibold text-[var(--text-primary)]">Memory</h5>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Store important project information—characters, story details, relationships—that the AI can reference during conversations.
                    </p>
                  </div>
                  
                  <div className="border-l-2 border-[var(--accent)] pl-4">
                    <h5 className="font-semibold text-[var(--text-primary)]">References</h5>
                    <p className="text-[var(--text-secondary)] text-sm">
                      Generate and manage AI-created reference images for your manga panels.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-[var(--bg-card)] rounded-lg p-4 border border-[var(--border)]">
                <h4 className="font-semibold text-[var(--text-primary)] mb-2">Quick Tips</h4>
                <ul className="text-[var(--text-secondary)] text-sm space-y-1">
                  <li>• Use the sidebar to navigate between sections</li>
                  <li>• Toggle dark/light mode using the button in the header</li>
                  <li>• Start by creating your first project</li>
                  <li>• Features marked as coming soon will be available in future updates</li>
                </ul>
              </div>
              
              <button
                onClick={handleDismissTutorial}
                className="w-full bg-[var(--accent)] text-white py-3 rounded-lg hover:opacity-90 transition"
              >
                Got it, let's start!
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

export default Home;
