import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/services';
import toast from 'react-hot-toast';
import { UserPlus, Mail, Lock, User, Eye, EyeOff, Loader2 } from 'lucide-react';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPwd, setShowPwd] = useState(false);
  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '',
    password: '', password2: '',
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    try {
      await authAPI.register(form);
      toast.success('Account created! Logging you in…');
      await login({ username: form.username, password: form.password });
      navigate('/dashboard');
    } catch (err) {
      const data = err.response?.data;
      if (data?.errors && Object.keys(data.errors).length > 0) {
        setErrors(data.errors);
      } else {
        toast.error(data?.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-circles">
        <div className="circle circle-1" />
        <div className="circle circle-2" />
        <div className="circle circle-3" />
      </div>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <span className="logo-icon">T</span>
          </div>
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join TaskManager and boost your productivity</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <div className="input-wrapper">
                <User size={16} className="input-icon" />
                <input
                  id="first_name" name="first_name" type="text"
                  placeholder="John" value={form.first_name}
                  onChange={handleChange} className={errors.first_name ? 'error' : ''}
                />
              </div>
              {errors.first_name && <span className="field-error">{errors.first_name}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <div className="input-wrapper">
                <User size={16} className="input-icon" />
                <input
                  id="last_name" name="last_name" type="text"
                  placeholder="Doe" value={form.last_name}
                  onChange={handleChange} className={errors.last_name ? 'error' : ''}
                />
              </div>
              {errors.last_name && <span className="field-error">{errors.last_name}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="username">Username <span className="required">*</span></label>
            <div className="input-wrapper">
              <User size={16} className="input-icon" />
              <input
                id="username" name="username" type="text" required
                placeholder="johndoe" value={form.username}
                onChange={handleChange} className={errors.username ? 'error' : ''}
              />
            </div>
            {errors.username && <span className="field-error">{Array.isArray(errors.username) ? errors.username[0] : errors.username}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email <span className="required">*</span></label>
            <div className="input-wrapper">
              <Mail size={16} className="input-icon" />
              <input
                id="email" name="email" type="email" required
                placeholder="john@example.com" value={form.email}
                onChange={handleChange} className={errors.email ? 'error' : ''}
              />
            </div>
            {errors.email && <span className="field-error">{Array.isArray(errors.email) ? errors.email[0] : errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password <span className="required">*</span></label>
            <div className="input-wrapper">
              <Lock size={16} className="input-icon" />
              <input
                id="password" name="password" type={showPwd ? 'text' : 'password'} required
                placeholder="Min. 8 characters" value={form.password}
                onChange={handleChange} className={errors.password ? 'error' : ''}
              />
              <button type="button" className="pwd-toggle" onClick={() => setShowPwd(!showPwd)}>
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <span className="field-error">{Array.isArray(errors.password) ? errors.password[0] : errors.password}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password2">Confirm Password <span className="required">*</span></label>
            <div className="input-wrapper">
              <Lock size={16} className="input-icon" />
              <input
                id="password2" name="password2" type={showPwd ? 'text' : 'password'} required
                placeholder="Repeat password" value={form.password2}
                onChange={handleChange} className={errors.password2 ? 'error' : ''}
              />
            </div>
            {errors.password2 && <span className="field-error">{Array.isArray(errors.password2) ? errors.password2[0] : errors.password2}</span>}
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <Loader2 size={18} className="spin" /> : <UserPlus size={18} />}
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
