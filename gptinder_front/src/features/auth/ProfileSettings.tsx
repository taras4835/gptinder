import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store/store';
import { updateProfile, updatePassword, clearError } from './authSlice';

const ProfileSettings = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, isLoading, error } = useSelector((state: RootState) => state.auth);
  
  const [profileData, setProfileData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    bio: '',
    interests: '',
  });
  
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Load user data into the form when component mounts
  useEffect(() => {
    if (user) {
      setProfileData({
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        bio: user.bio || '',
        interests: user.interests || '',
      });
      
      // Set profile picture preview if available
      if (user.profile_picture) {
        setPreviewUrl(user.profile_picture);
      }
    }
  }, [user]);
  
  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };
  
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setProfilePicture(file);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(clearError());
    setSuccessMessage(null);
    
    const data = new FormData();
    
    // Add form data
    Object.entries(profileData).forEach(([key, value]) => {
      data.append(key, value);
    });
    
    // Add profile picture if available
    if (profilePicture) {
      data.append('profile_picture', profilePicture);
    }
    
    const result = await dispatch(updateProfile(data));
    if (updateProfile.fulfilled.match(result)) {
      setSuccessMessage('Profile updated successfully');
    }
  };
  
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(clearError());
    setSuccessMessage(null);
    
    // Check if passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      // Handle mismatch
      return;
    }
    
    const result = await dispatch(updatePassword({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password
    }));
    
    if (updatePassword.fulfilled.match(result)) {
      setSuccessMessage('Password updated successfully');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto p-8 bg-white rounded-lg shadow-md">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Profile Settings</h2>
          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}
          {successMessage && (
            <div className="mt-4 p-3 bg-green-100 text-green-700 rounded-md">
              {successMessage}
            </div>
          )}
        </div>
        
        <div className="flex border-b border-gray-200 mb-6">
          <button
            className={`px-4 py-2 font-medium text-sm ${
              activeTab === 'profile' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('profile')}
          >
            Profile Information
          </button>
          <button
            className={`px-4 py-2 font-medium text-sm ${
              activeTab === 'password' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('password')}
          >
            Change Password
          </button>
        </div>
        
        {activeTab === 'profile' && (
          <form onSubmit={handleProfileSubmit}>
            <div className="space-y-6">
              <div className="flex items-center">
                <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-100 mr-4">
                  {previewUrl ? (
                    <img 
                      src={previewUrl} 
                      alt="Profile preview" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-indigo-100 text-indigo-700 text-xl font-bold">
                      {user?.username?.charAt(0).toUpperCase() || '?'}
                    </div>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Profile Picture
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="mt-1"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  className="input-field"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                    First Name
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={profileData.first_name}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
                
                <div>
                  <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                    Last Name
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={profileData.last_name}
                    onChange={handleProfileChange}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                  Bio
                </label>
                <textarea
                  id="bio"
                  name="bio"
                  rows={3}
                  value={profileData.bio}
                  onChange={handleProfileChange}
                  className="input-field"
                />
              </div>
              
              <div>
                <label htmlFor="interests" className="block text-sm font-medium text-gray-700">
                  Interests
                </label>
                <textarea
                  id="interests"
                  name="interests"
                  rows={3}
                  value={profileData.interests}
                  onChange={handleProfileChange}
                  className="input-field"
                  placeholder="Share your interests, separated by commas"
                />
              </div>
              
              <div>
                <button 
                  type="submit" 
                  className="btn-primary w-full sm:w-auto"
                  disabled={isLoading}
                >
                  {isLoading ? 'Saving...' : 'Save Profile'}
                </button>
              </div>
            </div>
          </form>
        )}
        
        {activeTab === 'password' && (
          <form onSubmit={handlePasswordSubmit}>
            <div className="space-y-6">
              <div>
                <label htmlFor="current_password" className="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <input
                  type="password"
                  id="current_password"
                  name="current_password"
                  value={passwordData.current_password}
                  onChange={handlePasswordChange}
                  required
                  className="input-field"
                />
              </div>
              
              <div>
                <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <input
                  type="password"
                  id="new_password"
                  name="new_password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  required
                  className="input-field"
                />
              </div>
              
              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirm_password"
                  name="confirm_password"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordChange}
                  required
                  className="input-field"
                />
                {passwordData.new_password !== passwordData.confirm_password && passwordData.confirm_password && (
                  <p className="mt-1 text-sm text-red-600">Passwords must match</p>
                )}
              </div>
              
              <div>
                <button 
                  type="submit" 
                  className="btn-primary w-full sm:w-auto"
                  disabled={
                    isLoading || 
                    !passwordData.current_password || 
                    !passwordData.new_password ||
                    passwordData.new_password !== passwordData.confirm_password
                  }
                >
                  {isLoading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ProfileSettings; 