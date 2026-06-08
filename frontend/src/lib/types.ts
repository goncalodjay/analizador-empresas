export interface UserOut {
  id: string;
  email: string;
  timezone: string;
  risk_tolerance: string;
  email_notifications: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}
