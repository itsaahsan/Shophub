import React from 'react';
import { Link } from 'react-router-dom';
import { Star, ShoppingCart, Heart } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Product } from '../../types';
import { useCartStore } from '../../stores/cartStore';
import { useAuthStore } from '../../stores/authStore';
import { wishlistApi } from '../../services/api';
import toast from 'react-hot-toast';

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const addItem = useCartStore((state) => state.addItem);
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const wishlistMutation = useMutation({
    mutationFn: () => wishlistApi.add(product.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      toast.success('Added to wishlist!');
    },
    onError: () => toast.error('Failed to add to wishlist'),
  });

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    addItem(product.id, 1);
    toast.success('Added to cart!');
  };

  const handleAddToWishlist = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) {
      toast.error('Please login to use wishlist');
      return;
    }
    wishlistMutation.mutate();
  };

  const primaryImage =
    (product.original_images && product.original_images[0]) ||
    product.images[0] ||
    `https://placehold.co/400x500/f3f4f6/9ca3af?text=${encodeURIComponent(product.name.slice(0, 20))}`;

  return (
    <div className="group relative bg-white rounded-2xl border border-border overflow-hidden transition-all duration-300 hover:shadow-hover hover:-translate-y-1">
      {/* Wishlist Button */}
      <button
        onClick={handleAddToWishlist}
        className="absolute top-3 right-3 z-10 p-2 bg-white/80 backdrop-blur-sm rounded-full text-muted hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 shadow-sm border border-border"
      >
        <Heart className="w-4 h-4" />
      </button>

      <Link to={`/product/${product.id}`} className="block">
        {/* Image Container */}
        <div className="aspect-[4/5] bg-card overflow-hidden relative">
          <img
            src={primaryImage}
            alt={product.name}
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).src = `https://placehold.co/400x500/f3f4f6/9ca3af?text=${encodeURIComponent(
                product.name.slice(0, 20),
              )}`;
            }}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          
          {/* Quick Add Overlay */}
          <div className="absolute inset-x-0 bottom-0 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
            <button
              onClick={handleAddToCart}
              className="w-full bg-primary text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 shadow-lg"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Quick Add</span>
            </button>
          </div>
        </div>
        
        {/* Info Container */}
        <div className="p-4 bg-white">
          <div className="flex items-center justify-between mb-1">
            <p className="text-[11px] font-extrabold uppercase tracking-widest text-muted">{product.category}</p>
            <div className="flex items-center text-yellow-400">
              <Star className="w-3 h-3 fill-current" />
              <span className="text-[11px] font-bold text-primary ml-1">{product.average_rating.toFixed(1)}</span>
            </div>
          </div>
          
          <h3 className="text-[15px] font-bold text-primary line-clamp-1 mb-1 group-hover:text-accent transition-colors">
            {product.name}
          </h3>
          
          <div className="flex items-center justify-between mt-3">
            <span className="text-lg font-extrabold text-success">
              ${product.price.toFixed(2)}
            </span>
            <span className="text-[10px] text-muted font-medium">Free Shipping</span>
          </div>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;
