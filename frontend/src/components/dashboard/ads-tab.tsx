"use client"
import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import axios from 'axios';
import { BACKEND_URL } from '@/lib/config';

interface GeneratedImage {
  url: string;
  prompt: string;
}

interface ApiResponse {
  category: string;
  failed_generations: string[];
  generated_images: Array<{
    image: string;
    prompt: string;
  }>;
}

const categories = [
  'Informative Content',
  'Motivational',
  'Tech Reviews'
];

export function AdsTab() {
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!selectedCategory) {
      setError('Please select a category.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await axios.get<ApiResponse>(`${BACKEND_URL}/api/generate-ads/${selectedCategory}`);
      
      const processedImages = response.data.generated_images.map(item => ({
        url: item.image.startsWith('data:image') 
          ? item.image 
          : `data:image/png;base64,${item.image}`,
        prompt: item.prompt
      }));

      setImages(processedImages);
    } catch (err) {
      console.error('Error generating images:', err);
      setError('Failed to generate images. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        {/* Input Controls */}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Category</label>
            <Select 
              value={selectedCategory} 
              onValueChange={setSelectedCategory}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button 
            onClick={handleGenerate}
            disabled={isLoading || !selectedCategory}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Advertisements'
            )}
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-red-500 text-center">
            {error}
          </div>
        )}

        {/* Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image, index) => (
            <div key={index} className="flex flex-col space-y-2">
              <div className="relative aspect-square overflow-hidden rounded-lg">
                <img
                  src={image.url}
                  alt={`Generated ad ${index + 1}`}
                  className="object-cover w-full h-full hover:scale-105 transition-transform duration-200"
                />
              </div>
              <p className="text-sm text-gray-600 break-words">
                {image.prompt}
              </p>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {images.length === 0 && !isLoading && !error && (
          <div className="flex justify-center items-center h-[400px] text-gray-500">
            Select a category to generate advertisements
          </div>
        )}
      </div>
    </Card>
  );
}

export default AdsTab;