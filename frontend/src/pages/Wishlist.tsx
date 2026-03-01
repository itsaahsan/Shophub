import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { wishlistApi } from '../services/api';
import { WishlistItem } from '../types';
import { Heart, Trash2, ShoppingCart, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCartStore } from '../stores/cartStore';
import toast from 'react-hot-toast';

const Wishlist: React.FC = () => {
  const queryClient = useQueryClient();
  const addItem = useCartStore((state) => state.addItem);

  const { data, isLoading } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => wishlistApi.get().then(res => res.data),
  });

  const removeMutation = useMutation({
    mutationFn: (productId: string) => wishlistApi.remove(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      toast.success('Removed from wishlist');
    },
  });

  const handleMoveToCart = (item: WishlistItem) => {
    addItem(item.product_id, 1);
    removeMutation.mutate(item.product_id);
    toast.success('Moved to cart!');
  };

  return (
    <div className="container mx-auto px-4 py-10">
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse space-y-4">
              <div className="aspect-[4/5] bg-card rounded-2xl"></div>
              <div className="h-4 bg-card rounded w-3/4"></div>
            </div>
          ))}
        </div>
      ) : !data?.items || data.items.length === 0 ? (
        <div className="text-center py-24 bg-card rounded-[3rem] border border-border border-dashed">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-subtle border border-border">
            <Heart className="w-10 h-10 text-gray-200" />
          </div>
          <h2 className="text-2xl font-bold text-primary mb-2">Your wishlist is empty</h2>
          <p className="text-muted mb-10 max-w-xs mx-auto">Start exploring and save items you love to your personal wishlist.</p>
          <Link to="/" className="btn-primary inline-flex items-center px-8">
            Browse Products <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {data.items.map((item: WishlistItem) => (
            <div key={item.product_id} className="group bg-white rounded-2xl border border-border overflow-hidden transition-all duration-300 hover:shadow-hover hover:-translate-y-1">
              <Link to={`/product/${item.product_id}`} className="block">
                <div className="aspect-[4/5] bg-card overflow-hidden">
                  <img
                    src={item.image || `https://placehold.co/400x500/f3f4f6/9ca3af?text=${encodeURIComponent(item.name.slice(0, 20))}`}
                    alt={item.name}
                    loading="lazy"
                    onError={(e) => { (e.target as HTMLImageElement).src = `https://placehold.co/400x500/f3f4f6/9ca3af?text=${encodeURIComponent(item.name.slice(0, 20))}`; }}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                </div>
              </Link>

              <div className="p-4 space-y-3">
                <Link to={`/product/${item.product_id}`}>
                  <h3 className="text-[15px] font-bold text-primary line-clamp-1 group-hover:text-accent transition-colors">
                    {item.name}
                  </h3>
                </Link>
                <span className="text-lg font-extrabold text-success block">${item.price.toFixed(2)}</span>
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => handleMoveToCart(item)}
                    className="btn-primary flex-1 text-xs h-9"
                  >
                    <ShoppingCart className="w-3.5 h-3.5 mr-1.5" /> Add to Cart
                  </button>
                  <button
                    onClick={() => removeMutation.mutate(item.product_id)}
                    className="p-2 border border-border rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Wishlist;
