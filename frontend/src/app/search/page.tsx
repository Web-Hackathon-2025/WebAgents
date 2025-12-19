"use client";

import { useEffect, useState } from "react";
import { useSearchStore } from "@/stores/search-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { RatingDisplay } from "@/components/shared/rating-display";
import { formatDistance } from "@/lib/utils/distance";
import { formatCurrency } from "@/lib/utils/format";
import { Search as SearchIcon, MapPin, Star, Filter, CheckCircle2, Phone } from "lucide-react";
import Link from "next/link";
import { useDebounce } from "@/hooks/use-debounce";
import { mockProviders, mockDataService } from "@/lib/mock-data";

export default function SearchPage() {
  const { query, filters, results, isLoading, setQuery, setFilters, search } = useSearchStore();
  const [searchInput, setSearchInput] = useState(query);
  const [mockResults, setMockResults] = useState(mockProviders);
  const [isLoadingMock, setIsLoadingMock] = useState(false);
  const debouncedQuery = useDebounce(searchInput, 500);

  useEffect(() => {
    setQuery(debouncedQuery);
  }, [debouncedQuery, setQuery]);

  useEffect(() => {
    if (mockDataService.isMockModeEnabled()) {
      handleMockSearch();
    } else {
      search();
    }
  }, [query, filters]);

  const handleMockSearch = async () => {
    setIsLoadingMock(true);
    // Simulate search delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    let filtered = mockProviders;
    
    if (searchInput) {
      const searchLower = searchInput.toLowerCase();
      filtered = mockProviders.filter(provider => 
        provider.businessName.toLowerCase().includes(searchLower) ||
        provider.fullName.toLowerCase().includes(searchLower) ||
        provider.serviceCategories.some(cat => cat.toLowerCase().includes(searchLower)) ||
        provider.businessAddress.address.toLowerCase().includes(searchLower)
      );
    }
    
    setMockResults(filtered);
    setIsLoadingMock(false);
  };

  const handleSearch = () => {
    if (mockDataService.isMockModeEnabled()) {
      handleMockSearch();
    } else {
      search();
    }
  };

  const displayResults = mockDataService.isMockModeEnabled() ? mockResults : results;
  const displayLoading = mockDataService.isMockModeEnabled() ? isLoadingMock : isLoading;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-4 text-3xl font-bold text-text-primary">Find Service Providers</h1>
        
        {/* Search Bar */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-text-secondary" />
            <Input
              placeholder="Search for services..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button onClick={handleSearch}>
            <SearchIcon className="mr-2 h-4 w-4" />
            Search
          </Button>
        </div>

        {/* Filters */}
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="outline" className="cursor-pointer">
            All Categories
          </Badge>
          <Badge variant="outline" className="cursor-pointer">
            Plumbing
          </Badge>
          <Badge variant="outline" className="cursor-pointer">
            Electrical
          </Badge>
          <Badge variant="outline" className="cursor-pointer">
            Carpentry
          </Badge>
          <Button variant="ghost" size="sm">
            <Filter className="mr-2 h-4 w-4" />
            More Filters
          </Button>
        </div>
      </div>

      {/* Results */}
      {displayLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : !displayResults || displayResults.length === 0 ? (
        <EmptyState
          icon={<SearchIcon className="h-12 w-12 text-gray-400" />}
          title="No providers found"
          description="Try adjusting your search criteria or filters"
        />
      ) : (
        <>
          <div className="flex items-center justify-between mb-6">
            <p className="text-sm text-gray-600">
              Found {displayResults.length} provider{displayResults.length !== 1 ? "s" : ""}
            </p>
            {mockDataService.isMockModeEnabled() && (
              <Badge variant="secondary" className="bg-green-100 text-green-700">
                Demo Data
              </Badge>
            )}
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {displayResults.map((provider) => (
              <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={provider.avatar} alt={provider.fullName} />
                      <AvatarFallback>
                        {provider.fullName.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg">{provider.businessName}</CardTitle>
                      <CardDescription className="mt-1">
                        {provider.fullName}
                      </CardDescription>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {provider.serviceCategories?.slice(0, 2).map((category) => (
                          <Badge key={category} variant="secondary" className="text-xs">
                            {category.replace('-', ' ')}
                          </Badge>
                        ))}
                        {provider.serviceCategories && provider.serviceCategories.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{provider.serviceCategories.length - 2}
                          </Badge>
                        )}
                      </div>
                    </div>
                    {provider.isVerified && (
                      <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {provider.rating && (
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-semibold">{provider.rating}</span>
                          <span className="text-gray-500 text-sm">({provider.reviewCount} reviews)</span>
                        </div>
                      </div>
                    )}
                    
                    {provider.businessAddress?.address && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <MapPin className="h-4 w-4 flex-shrink-0" />
                        <span className="truncate">{provider.businessAddress.address}</span>
                      </div>
                    )}

                    {provider.phone && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Phone className="h-4 w-4 flex-shrink-0" />
                        <span>{provider.phone}</span>
                      </div>
                    )}

                    {provider.serviceRadius && (
                      <div className="text-sm text-gray-600">
                        Service Radius: {provider.serviceRadius} km
                      </div>
                    )}

                    <div className="pt-2">
                      <Button asChild className="w-full">
                        <Link href={`/providers/${provider.id}`}>View Profile</Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

