import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import axios from 'axios';
import { Loader2 } from 'lucide-react';
import { BACKEND_URL } from '@/lib/config';

interface AdsTabProps {
  category: string;
}

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

export function AdsTab({ category }: AdsTabProps) {
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await axios.get<ApiResponse>(`${BACKEND_URL}/api/generate-ads/${category}`);
        
        // Process the images
        const processedImages = response.data.generated_images.map(item => {
          const fullBase64Data = item.image.startsWith('data:image') 
            ? item.image 
            : `data:image/png;base64,${item.image}`;
            
          return {
            url: fullBase64Data,
            prompt: item.prompt
          };
        });

        setImages(processedImages);
      } catch (err) {
        console.error('Error fetching images:', err);
        setError('Failed to load images. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchImages();
  }, [category]);

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex flex-col items-center justify-center h-[600px] space-y-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-gray-500">Generating advertisements...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex flex-col items-center justify-center h-[600px] text-red-500">
          {error}
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
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
      {images.length === 0 && !isLoading && !error && (
        <div className="flex justify-center items-center h-[600px] text-gray-500">
          No advertisements generated yet.
        </div>
      )}
    </Card>
  );
}

export default AdsTab;