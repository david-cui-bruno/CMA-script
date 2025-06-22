import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfile: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="relative">
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
            <span className="text-sm font-medium text-white">
              {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
            </span>
          </div>
        </div>
        <div className="hidden md:block">
          <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
          <div className="text-sm text-gray-500">{user.company || 'Real Estate Professional'}</div>
        </div>
        <button
          onClick={logout}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          title="Sign out"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default UserProfile; 