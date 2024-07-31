import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaDownload, FaInfoCircle, FaImage, FaMusic, FaPalette, FaQuestionCircle } from 'react-icons/fa';
import './tailwind.css'; 
import './output.css'; 
import mainApp from './mainApp.png'; 
import deckEdit from './deckEdit.png'; 
import GCPLogo from './GCPLogo.png'; 

const App = () => {
  const [isOverlayVisible, setIsOverlayVisible] = useState(false);
  const [copyWindows, setCopyWindows] = useState(false);
  const [copyLinux, setCopyLinux] = useState(false);

  const windowsCommand = 'curl -o gcpstudio.py https://fayaz.one/gcpstudio/gcpstudio.py && python gcpstudio.py';
  const macCommand = 'curl -O https://fayaz.one/gcpstudio/gcpstudio.py && python3 gcpstudio.py';


  useEffect(() => {
    // Optional: If you need to perform any actions when the component mounts.
  }, []);

  const handleDownloadClick = () => {
    setIsOverlayVisible(true);
  };

  const handleCloseOverlay = () => {
    setIsOverlayVisible(false);
  };

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    if (text===windowsCommand) {
      setCopyWindows(true);
      setTimeout(() => setCopyWindows(false), 2000);
    }
    else if (text===macCommand) {
      setCopyLinux(true);
      setTimeout(() => setCopyLinux(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 via-purple-700 to-purple-900 text-white">
      <header className="container mx-auto py-8">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <img src={GCPLogo} alt="GCP Logo" className="mx-auto mb-4" />
          <h1 className="text-5xl font-extrabold">Version 1.0.0</h1>
        </motion.div>
      </header>

      <main className="container mx-auto mt-12">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <button 
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-full inline-flex items-center transition duration-300"
            onClick={handleDownloadClick}
          >
            <FaDownload className="mr-2" />
            Download Now
          </button>
        </motion.div>

        <motion.div 
          className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <FeatureCard 
            icon={<FaImage />}
            title="Custom Images"
            description="Add unique images to each trivia card to make your questions more engaging."
          />
          <FeatureCard 
            icon={<FaMusic />}
            title="Sound Integration"
            description="Incorporate sound files to play in the background of each card for an immersive experience."
          />
          <FeatureCard 
            icon={<FaPalette />}
            title="Category Customization"
            description="Create and customize categories with unique names and color schemes."
          />
          <FeatureCard 
            icon={<FaQuestionCircle />}
            title="Flexible Question Format"
            description="Design questions with multiple hints for progressive difficulty."
          />
          <FeatureCard 
            icon={<FaInfoCircle />}
            title="Easy-to-Use Interface"
            description="Intuitive design makes creating and editing card packs a breeze."
          />
        </motion.div>

        <motion.div 
          className="mt-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <h2 className="text-3xl font-bold mb-4">Screenshots</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <img src={mainApp} alt="GCP Studio Interface" className="rounded-lg shadow-lg" />
            <img src={deckEdit} alt="Card Editing" className="rounded-lg shadow-lg" />
          </div>
        </motion.div>

        <motion.div 
          className="mt-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
        >
          <h2 className="text-3xl font-bold mb-4">Documentation</h2>
          <div className="bg-white bg-opacity-20 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-2">Getting Started</h3>
            <ol className="list-decimal list-inside space-y-2">
              <li>Download GCP Studio from the button above.</li>
              <li>Run the Python script to launch the application.</li>
              <li>Create a new card pack or open an existing one.</li>
              <li>Add categories, questions, hints, images, and sounds to your pack.</li>
              <li>Save your pack and use it in your trivia game!</li>
            </ol>
            <a href="/full-documentation" className="text-blue-300 hover:text-blue-100 mt-4 inline-block">View Full Documentation</a>
          </div>
        </motion.div>
      </main>

      <footer className="container mx-auto mt-16 py-8 text-center">
        <p>&copy; 2024 GCP Studio. All rights reserved.</p>
      </footer>

      {/* Overlay for download instructions */}
      {isOverlayVisible && (
        <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-80 z-50">
          <div className="bg-white p-8 rounded-lg text-black max-w-md mx-auto relative">
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
              onClick={handleCloseOverlay}
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4">How to Run GCP Studio</h2>
            <p className="mb-4">Follow the instructions below to run GCP Studio:</p>
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Windows (Command Prompt):</h3>
              <p className="bg-gray-100 p-2 rounded mb-2">
                {windowsCommand}
              </p>
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={() => handleCopyToClipboard(windowsCommand, 'windows')}
              >
                {copyWindows ? 'Copied!' : 'Copy Command'}
              </button>

              <div>
                <h3 className="text-lg font-semibold">macOS/Linux:</h3>
                <p className="bg-gray-100 p-2 rounded mb-2">
                  {macCommand}
                </p>
                <button
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                  onClick={() => handleCopyToClipboard(macCommand, 'linux')}
                >
                  {copyLinux ? 'Copied!' : 'Copy Command'}
                </button>
              </div>
            </div>
            <div className="text-center mt-6">
            <p className="mb-4">Alternatively, use the button below to download the Python script.</p>
              <a
                href="https://fayaz.one/gcpstudio/gcpstudio.py"
                download="gcpstudio.py"
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
              >
                Download Python Script
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <motion.div 
    className="bg-white bg-opacity-20 p-6 rounded-lg"
    whileHover={{ scale: 1.05 }}
    transition={{ duration: 0.3 }}
  >
    <div className="text-4xl mb-4">{icon}</div>
    <h3 className="text-xl font-semibold mb-2">{title}</h3>
    <p>{description}</p>
  </motion.div>
);

export default App;
