import React, { useState } from 'react';

const ToxicityModal = ({ isOpen, onClose, onConfirm, message, details }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-3xl">⚠️</span>
          <h3 className="text-xl font-bold text-gray-900">Content Warning</h3>
        </div>
        
        <p className="text-gray-700 mb-4 leading-relaxed">{message}</p>

        {details && (
          <div className="mb-6 text-sm text-gray-700 space-y-2">
            <div>
              <span className="font-semibold text-insta-pink">Detected category:</span>{' '}
              <span>{details.dominant_category || 'unknown'}</span>
            </div>
            <div>
              <span className="font-semibold text-insta-pink">Score:</span>{' '}
              <span>{typeof details.combined_score === 'number' ? details.combined_score.toFixed(3) : 'n/a'}</span>
            </div>
            {details.rule_categories && (
              <div>
                <span className="font-semibold text-insta-pink">Why flagged:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {Object.entries(details.rule_categories)
                    .filter(([_, v]) => v > 0)
                    .sort((a, b) => b[1] - a[1])
                    .map(([k, v]) => (
                      <span key={k} className="px-2 py-0.5 bg-insta-purple/10 text-insta-purple rounded-full">
                        {k}
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            No, Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-3 bg-gradient-to-r from-insta-purple to-insta-pink text-white rounded-lg font-semibold hover:opacity-90 transition"
          >
            Yes, Post Anyway
          </button>
        </div>
      </div>
    </div>
  );
};

export default ToxicityModal;
