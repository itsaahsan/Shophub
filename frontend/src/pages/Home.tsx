import React, { useState, useCallback } from 'react';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import api from '../lib/axios';
import ProductCard from '../components/product/ProductCard';
import { Product } from '../types';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Sparkles, Loader2 } from 'lucide-react';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('');

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const { data } = await api.get('/products/categories');
      return data as string[];
    },
  });

  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['products', selectedCategory],
    queryFn: async ({ pageParam = 1 }) => {
      const params: any = { page: pageParam };
      if (selectedCategory) params.category = selectedCategory;
      const { data } = await api.get('/products', { params });
      return data;
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.pages) return lastPage.page + 1;
      return undefined;
    },
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const { data } = await api.get('/recommendations');
      return data;
    },
  });

  const allProducts = data?.pages.flatMap((page: any) => page.products) || [];
  const total = data?.pages[0]?.total || 0;

  const handleCategoryClick = useCallback((cat: string) => {
    setSelectedCategory(cat === selectedCategory ? '' : cat);
  }, [selectedCategory]);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center">
        <div className="w-12 h-12 bg-gray-200 rounded-full mb-4"></div>
        <div className="h-4 w-32 bg-gray-200 rounded"></div>
      </div>
    </div>
  );
  
  if (error) return <div className="text-center py-20 text-red-600">Failed to load products.</div>;

  // Show a subset of categories as filter pills
  const filterCategories = categories || [];

  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-24 text-center">
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-[50%] top-0 h-[800px] w-[800px] -translate-x-1/2 rounded-full bg-accent/5 blur-3xl"></div>
        </div>
        
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="inline-flex items-center space-x-2 bg-accent/10 text-accent px-4 py-1.5 rounded-full text-xs font-bold mb-8 animate-in fade-in zoom-in duration-500">
            <Sparkles className="w-3 h-3" />
            <span>AI-POWERED SHOPPING EXPERIENCE</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter text-primary mb-6 leading-[1.1] animate-in fade-in slide-in-from-bottom-4 duration-700">
            Elevate Your Tech. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-indigo-400">Powered by Intelligence.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed animate-in fade-in slide-in-from-bottom-6 duration-1000">
            Shophub uses cutting-edge AI to recommend products that perfectly match your lifestyle. High quality tech, seamlessly delivered.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <button
              onClick={() => navigate('/search')}
              className="btn-primary w-full sm:w-auto h-12 px-10 text-base shadow-lg shadow-primary/20"
            >
              Explore Catalog
            </button>
            <button
              onClick={() => {
                const el = document.getElementById('trending');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="btn-secondary w-full sm:w-auto h-12 px-10 text-base flex items-center"
            >
              Browse Trending <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </section>


      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <section className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-2xl font-extrabold text-primary tracking-tight">Picked For You</h2>
              <p className="text-sm text-muted">Based on your recent interests and purchases.</p>
            </div>
            <Link to="/search" className="text-accent text-sm font-bold hover:underline">See all matches</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
            {recommendations.slice(0, 4).map((product: Product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      )}

      {/* Main Grid */}
      <section id="trending" className="container mx-auto px-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-10 gap-4">
          <div>
            <h2 className="text-2xl font-extrabold text-primary tracking-tight">Trending Collections</h2>
            <p className="text-sm text-muted">{total} products across all categories.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleCategoryClick('')}
              className={`px-4 py-1.5 rounded-full text-xs font-bold border transition-colors ${
                !selectedCategory
                  ? 'bg-primary text-white border-primary'
                  : 'border-border bg-white hover:border-primary'
              }`}
            >
              All
            </button>
            {filterCategories.map((cat: string) => (
              <button
                key={cat}
                onClick={() => handleCategoryClick(cat)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold border transition-colors ${
                  selectedCategory === cat
                    ? 'bg-primary text-white border-primary'
                    : 'border-border bg-white hover:border-primary'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {allProducts.map((product: Product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
        
        {hasNextPage && (
          <div className="mt-16 text-center">
            <button
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="btn-secondary h-12 px-12 text-sm font-bold mx-auto inline-flex items-center"
            >
              {isFetchingNextPage ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Loading...</>
              ) : (
                `Load More Products (${allProducts.length} of ${total})`
              )}
            </button>
          </div>
        )}
      </section>

    </div>
  );
};

export default Home;
