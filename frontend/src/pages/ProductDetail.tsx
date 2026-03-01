import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Star, ShoppingCart, Truck, RotateCcw, Share2, Info } from 'lucide-react';
import { productApi, reviewApi } from '../services/api';
import { useCartStore } from '../stores/cartStore';
import { useAuthStore } from '../stores/authStore';
import ProductCard from '../components/product/ProductCard';
import toast from 'react-hot-toast';

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const addItem = useCartStore((state) => state.addItem);
  const user = useAuthStore((state) => state.user);
  const [quantity, setQuantity] = useState(1);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewRating, setReviewRating] = useState(5);
  const [activeImage, setActiveImage] = useState(0);

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.get(id!).then(res => res.data),
    enabled: !!id,
  });

  const { data: similar } = useQuery({
    queryKey: ['product', id, 'similar'],
    queryFn: () => productApi.getSimilar(id!).then(res => res.data),
    enabled: !!id,
  });

  const { data: reviews } = useQuery({
    queryKey: ['reviews', id],
    queryFn: () => reviewApi.list(id!).then(res => res.data),
    enabled: !!id,
  });

  const reviewMutation = useMutation({
    mutationFn: (data: any) => reviewApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', id] });
      queryClient.invalidateQueries({ queryKey: ['product', id] });
      setReviewComment('');
      toast.success('Review submitted!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to submit review');
    }
  });

  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Loading details...</div>;
  if (!product) return <div className="text-center py-20">Product not found.</div>;

  const galleryImages: string[] =
    (product.original_images && product.original_images.length > 0
      ? product.original_images
      : product.images) || [];

  const handleAddToCart = () => {
    addItem(product.id, quantity);
    toast.success('Added to cart!');
  };

  const handleReviewSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return toast.error('Please login to review');
    reviewMutation.mutate({ product_id: product.id, rating: reviewRating, comment: reviewComment });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-20">
      {/* Breadcrumbs */}
      <nav className="flex items-center space-x-2 text-xs font-bold uppercase tracking-widest text-muted">
        <Link to="/" className="hover:text-primary transition-colors">Home</Link>
        <span>/</span>
        <Link to={`/search?category=${product.category}`} className="hover:text-primary transition-colors">{product.category}</Link>
        <span>/</span>
        <span className="text-primary truncate max-w-[200px]">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
        {/* Left: Images (Amazon Style) */}
        <div className="lg:col-span-7 flex flex-col md:flex-row gap-6">
          <div className="order-2 md:order-1 flex md:flex-col gap-3">
            {galleryImages.map((img: string, idx: number) => (
              <button 
                key={idx} 
                onClick={() => setActiveImage(idx)}
                className={`w-16 h-16 rounded-xl border-2 overflow-hidden bg-white transition-all ${activeImage === idx ? 'border-accent shadow-lg shadow-accent/10' : 'border-border hover:border-muted'}`}
              >
                <img src={img} alt="" loading="lazy" onError={(e) => { (e.target as HTMLImageElement).src = 'https://placehold.co/64x64/f3f4f6/9ca3af?text=No+img'; }} className="w-full h-full object-contain p-1" />
              </button>
            ))}
          </div>
          <div className="order-1 md:order-2 flex-1 bg-white rounded-[2rem] border border-border p-8 relative group">
            <img
              src={
                galleryImages[activeImage] ||
                `https://placehold.co/600x600/f3f4f6/9ca3af?text=${encodeURIComponent(product.name.slice(0, 20))}`
              }
              alt={product.name}
              onError={(e) => {
                (e.target as HTMLImageElement).src = `https://placehold.co/600x600/f3f4f6/9ca3af?text=${encodeURIComponent(
                  product.name.slice(0, 20),
                )}`;
              }}
              className="w-full h-auto max-h-[600px] object-contain mx-auto"
            />
            <button className="absolute top-6 right-6 p-3 bg-white shadow-subtle rounded-full text-muted hover:text-primary transition-colors border border-border">
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right: Product Info */}
        <div className="lg:col-span-5 space-y-8">
          <div className="space-y-4">
            <div className="inline-flex items-center px-3 py-1 bg-accent/10 text-accent rounded-full text-[10px] font-extrabold uppercase tracking-widest">
              Top Rated in {product.category}
            </div>
            <h1 className="text-4xl font-extrabold text-primary tracking-tight leading-tight">{product.name}</h1>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <div className="flex text-yellow-400 mr-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`w-4 h-4 ${i < Math.floor(product.average_rating) ? 'fill-current' : 'text-gray-200'}`} />
                  ))}
                </div>
                <span className="text-sm font-bold text-primary">{product.average_rating.toFixed(1)}</span>
              </div>
              <div className="h-4 w-px bg-border"></div>
              <span className="text-sm font-bold text-muted hover:text-accent cursor-pointer transition-colors underline underline-offset-4">
                {product.review_count} Global Ratings
              </span>
            </div>
          </div>

          <div className="bg-card rounded-3xl p-8 border border-border space-y-8">
            <div className="flex items-baseline space-x-2">
              <span className="text-4xl font-extrabold text-success">${product.price.toFixed(2)}</span>
              <span className="text-sm text-muted line-through font-medium">${(product.price * 1.2).toFixed(2)}</span>
              <span className="text-xs font-extrabold text-success uppercase">Save 20%</span>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm font-bold px-1">
                <span>Quantity</span>
                <span className={product.stock > 0 ? 'text-success' : 'text-red-500'}>
                  {product.stock > 0 ? `${product.stock} units available` : 'Out of Stock'}
                </span>
              </div>
              <div className="flex space-x-4">
                <div className="flex bg-white border border-border rounded-2xl overflow-hidden shadow-subtle">
                  <button onClick={() => setQuantity(q => Math.max(1, q-1))} className="px-5 py-3 hover:bg-card transition-colors font-bold">-</button>
                  <span className="px-6 py-3 font-extrabold text-primary flex items-center justify-center min-w-[60px]">{quantity}</span>
                  <button onClick={() => setQuantity(q => q+1)} className="px-5 py-3 hover:bg-card transition-colors font-bold">+</button>
                </div>
                <button
                  onClick={handleAddToCart}
                  disabled={product.stock === 0}
                  className="btn-primary flex-1 h-[58px] text-base shadow-xl shadow-primary/20"
                >
                  <ShoppingCart className="w-5 h-5 mr-3" /> Add to Cart
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="flex items-center text-[11px] font-extrabold uppercase tracking-widest text-muted">
                <Truck className="w-4 h-4 mr-2 text-accent" /> Express Delivery
              </div>
              <div className="flex items-center text-[11px] font-extrabold uppercase tracking-widest text-muted">
                <RotateCcw className="w-4 h-4 mr-2 text-accent" /> 30-Day Returns
              </div>
            </div>
          </div>

          <div className="space-y-6 px-4">
            <div>
              <h3 className="text-sm font-extrabold uppercase tracking-widest text-primary mb-3">About this item</h3>
              <p className="text-[15px] text-muted leading-relaxed font-medium">{product.description}</p>
            </div>
            
            <div className="flex items-start p-4 bg-blue-50/50 rounded-2xl border border-blue-100">
              <Info className="w-4 h-4 text-blue-500 mr-3 mt-1" />
              <p className="text-xs text-blue-600 font-medium leading-relaxed">
                Prices and availability were last updated by our AI at {new Date().toLocaleTimeString()}. 
                Actual stock may vary based on your location.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Products */}
      {similar && similar.length > 0 && (
        <section className="pt-20 border-t border-border">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-2xl font-extrabold text-primary tracking-tight">AI-Matched Alternatives</h2>
              <p className="text-sm text-muted">Customers who viewed this also considered these items.</p>
            </div>
            <Link to="/search" className="text-accent text-sm font-bold hover:underline">See all matches</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
            {similar.map((p: any) => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}

      {/* Reviews Section */}
      <section className="pt-20 border-t border-border">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
          <div className="lg:col-span-4 space-y-8">
            <h2 className="text-2xl font-extrabold text-primary tracking-tight">Customer Reviews</h2>
            <div className="bg-card rounded-3xl p-8 border border-border">
              <div className="flex items-center space-x-4 mb-6">
                <span className="text-5xl font-extrabold text-primary">{product.average_rating.toFixed(1)}</span>
                <div>
                  <div className="flex text-yellow-400">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={`w-4 h-4 ${i < Math.floor(product.average_rating) ? 'fill-current' : 'text-gray-200'}`} />
                    ))}
                  </div>
                  <p className="text-xs font-bold text-muted mt-1 uppercase tracking-widest">Average Rating</p>
                </div>
              </div>
              <button className="btn-secondary w-full text-sm font-bold h-11" onClick={() => {
                const form = document.getElementById('review-form');
                if (form) form.scrollIntoView({ behavior: 'smooth' });
              }}>
                Write a Review
              </button>
            </div>
          </div>

          <div id="review-form" className="lg:col-span-8 space-y-8">
            {user && (
              <div className="bg-card rounded-3xl p-8 border border-border mb-8">
                <h3 className="font-bold mb-4">Post your review</h3>
                <form onSubmit={handleReviewSubmit} className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <label className="text-sm font-bold">Rating:</label>
                    <select 
                      value={reviewRating} 
                      onChange={(e) => setReviewRating(Number(e.target.value))}
                      className="bg-white border border-border rounded-lg px-3 py-1"
                    >
                      {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} Stars</option>)}
                    </select>
                  </div>
                  <textarea 
                    value={reviewComment} 
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="What did you think about this product?"
                    className="input-field h-32"
                    required
                  />
                  <button type="submit" disabled={reviewMutation.isPending} className="btn-primary">
                    {reviewMutation.isPending ? 'Posting...' : 'Submit Review'}
                  </button>
                </form>
              </div>
            )}
            {reviews?.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center py-20 bg-card rounded-[2.5rem] border border-border border-dashed">
                <p className="text-muted font-bold italic">No reviews yet. Be the first to share your thoughts!</p>
              </div>
            ) : (
              <div className="space-y-6">
                {reviews?.map((review: any) => (
                  <div key={review.id} className="bg-white p-8 rounded-3xl border border-border shadow-subtle group hover:border-accent transition-colors duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold text-xs border border-accent/20">
                          {review.user_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-bold text-primary text-sm">{review.user_name}</p>
                          <p className="text-[10px] text-muted font-bold uppercase tracking-widest">Verified Purchase</p>
                        </div>
                      </div>
                      <div className="flex text-yellow-400">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className={`w-3.5 h-3.5 ${i < review.rating ? 'fill-current' : 'text-gray-200'}`} />
                        ))}
                      </div>
                    </div>
                    <p className="text-[15px] text-primary leading-relaxed font-medium">{review.comment}</p>
                    <div className="mt-6 flex items-center text-[10px] font-bold text-muted uppercase tracking-widest">
                      <span>Posted on {new Date(review.created_at).toLocaleDateString()}</span>
                      <span className="mx-2">•</span>
                      <button className="hover:text-accent transition-colors">Helpful</button>
                      <span className="mx-2">•</span>
                      <button className="hover:text-red-500 transition-colors">Report</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default ProductDetail;
