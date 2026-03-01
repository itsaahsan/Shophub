import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi, productApi } from '../services/api';
import { Product } from '../types';
import { Plus, Edit2, Trash2, Search, X } from 'lucide-react';
import toast from 'react-hot-toast';

const ManageProducts: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 0,
    category: '',
    stock: 0,
    images: [] as string[]
  });

  const { data, isLoading } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => productApi.list({}).then(res => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => adminApi.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-products'] });
      setIsModalOpen(false);
      toast.success('Product created successfully');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string, data: any }) => adminApi.updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-products'] });
      setIsModalOpen(false);
      setEditingProduct(null);
      toast.success('Product updated successfully');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-products'] });
      toast.success('Product deleted');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingProduct) {
      updateMutation.mutate({ id: editingProduct.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const openEdit = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description,
      price: product.price,
      category: product.category,
      stock: product.stock,
      images: product.images
    });
    setIsModalOpen(true);
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Manage Products</h1>
          <p className="text-sm text-muted">Add, edit or remove products from your catalog.</p>
        </div>
        <button 
          onClick={() => {
            setEditingProduct(null);
            setFormData({ name: '', description: '', price: 0, category: '', stock: 0, images: [] });
            setIsModalOpen(true);
          }}
          className="btn-primary flex items-center shadow-lg shadow-primary/20"
        >
          <Plus className="w-4 h-4 mr-2" /> Add Product
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-border overflow-hidden shadow-subtle">
        <div className="p-4 border-b border-border bg-card/50">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input 
              type="text" 
              placeholder="Filter products..." 
              className="w-full pl-10 pr-4 py-2 bg-white border border-border rounded-xl text-sm outline-none" 
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-card/30 text-[10px] uppercase tracking-widest font-extrabold text-muted">
                <th className="px-6 py-4">Product</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Price</th>
                <th className="px-6 py-4">Stock</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data?.products.map((product: Product) => (
                <tr key={product.id} className="hover:bg-card/20 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <img
                        src={product.images[0] || `https://placehold.co/80x80/f3f4f6/9ca3af?text=${encodeURIComponent(product.name.slice(0, 10))}`}
                        alt={product.name}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = `https://placehold.co/80x80/f3f4f6/9ca3af?text=${encodeURIComponent(product.name.slice(0, 10))}`;
                        }}
                        className="w-10 h-10 rounded-lg border border-border object-contain p-1"
                      />
                      <span className="font-bold text-sm text-primary">{product.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted">{product.category}</td>
                  <td className="px-6 py-4 font-bold text-sm">${product.price.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${product.stock > 0 ? 'bg-success/10 text-success' : 'bg-red-50 text-red-500'}`}>
                      {product.stock} in stock
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button onClick={() => openEdit(product)} className="p-2 hover:bg-card rounded-lg text-muted transition-colors"><Edit2 className="w-4 h-4" /></button>
                      <button onClick={() => deleteMutation.mutate(product.id)} className="p-2 hover:bg-red-50 rounded-lg text-red-500 transition-colors"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-primary/20 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-2xl rounded-[2.5rem] border border-border shadow-2xl overflow-hidden animate-in slide-in-from-bottom-8 duration-300">
            <div className="px-8 py-6 border-b border-border flex items-center justify-between">
              <h2 className="text-xl font-bold">{editingProduct ? 'Edit Product' : 'Add New Product'}</h2>
              <button onClick={() => setIsModalOpen(false)} className="p-2 hover:bg-card rounded-xl transition-colors"><X className="w-5 h-5" /></button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-8 space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="col-span-2">
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Product Name</label>
                  <input required className="input-field" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                </div>
                <div className="col-span-2">
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Description</label>
                  <textarea required className="input-field h-32" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
                </div>
                <div>
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Price ($)</label>
                  <input type="number" step="0.01" required className="input-field" value={formData.price} onChange={e => setFormData({...formData, price: Number(e.target.value)})} />
                </div>
                <div>
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Stock</label>
                  <input type="number" required className="input-field" value={formData.stock} onChange={e => setFormData({...formData, stock: Number(e.target.value)})} />
                </div>
                <div className="col-span-2">
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Category</label>
                  <input required className="input-field" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} />
                </div>
                <div className="col-span-2">
                  <label className="text-[10px] font-extrabold uppercase tracking-widest text-muted block mb-2">Image URLs</label>
                  <textarea
                    className="input-field h-24 text-xs"
                    placeholder="Paste one or more direct image URLs, separated by commas"
                    value={formData.images.join(', ')}
                    onChange={e =>
                      setFormData({
                        ...formData,
                        images: e.target.value
                          .split(',')
                          .map((v) => v.trim())
                          .filter(Boolean),
                      })
                    }
                  />
                  <p className="mt-1 text-[10px] text-muted">
                    Example: https://res.cloudinary.com/.../image1.jpg, https://res.cloudinary.com/.../image2.jpg
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary flex-1 h-12">Cancel</button>
                <button type="submit" className="btn-primary flex-1 h-12">
                  {editingProduct ? 'Update Product' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageProducts;
