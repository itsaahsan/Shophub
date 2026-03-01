// User types
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  avatar?: string;
}

// Product types
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  stock: number;
  images: string[];
  original_images?: string[];
  average_rating: number;
  review_count: number;
  created_at: string;
}

// Cart types
export interface CartItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
  stock: number;
}

export interface Cart {
  user_id: string;
  items: CartItem[];
}

// Order types
export interface ShippingAddress {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
}

export interface OrderItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

export interface Order {
  id: string;
  user_id: string;
  items: OrderItem[];
  total: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  shipping_address: ShippingAddress;
  stripe_session_id?: string;
  created_at: string;
}

// Review types
export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

// Wishlist types
export interface WishlistItem {
  product_id: string;
  name: string;
  price: number;
  image?: string;
  added_at: string;
}

export interface Wishlist {
  user_id: string;
  items: WishlistItem[];
}

// Dashboard Stats
export interface AdminStats {
  total_revenue: number;
  total_sales: number;
  total_users: number;
  total_products: number;
  recent_orders: Order[];
  revenue_chart: { date: string; revenue: number }[];
}
