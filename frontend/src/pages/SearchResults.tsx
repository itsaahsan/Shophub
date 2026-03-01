import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInfiniteQuery } from '@tanstack/react-query';
import { productApi } from '../services/api';
import ProductCard from '../components/product/ProductCard';
import { Product } from '../types';
import { SlidersHorizontal, Search as SearchIcon, Loader2 } from 'lucide-react';

const SearchResults: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || '';
  const [sortBy, setSortBy] = useState('newest');

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['search', query, category, sortBy],
    queryFn: async ({ pageParam = 1 }) => {
      const res = await productApi.list({ search: query, category, sort: sortBy, page: pageParam });
      return res.data;
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.pages) return lastPage.page + 1;
      return undefined;
    },
  });

  const allProducts = data?.pages.flatMap((page: any) => page.products) || [];
  const total = data?.pages[0]?.total || 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-primary tracking-tight flex items-center">
            <SearchIcon className="w-6 h-6 mr-2 text-muted" />
            {query ? `Results for "${query}"` : category ? category : 'All Products'}
          </h1>
          <p className="text-muted text-sm mt-1">{total} products found</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-card border border-border px-3 py-2 rounded-xl">
            <SlidersHorizontal className="w-4 h-4 text-muted" />
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-sm font-bold focus:outline-none"
            >
              <option value="newest">Newest First</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
            </select>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse space-y-4">
              <div className="aspect-[4/5] bg-card rounded-2xl"></div>
              <div className="h-4 bg-card rounded w-3/4"></div>
              <div className="h-4 bg-card rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : allProducts.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-[2.5rem] border border-border border-dashed">
          <SearchIcon className="w-12 h-12 text-muted mx-auto mb-4 opacity-20" />
          <p className="text-muted font-bold">No products matched your search.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
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
        </>
      )}
    </div>
  );
};

export default SearchResults;
