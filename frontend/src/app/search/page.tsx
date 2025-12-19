"use client";

import { useEffect, useState } from "react";
import { useSearchStore } from "@/stores/search-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { RatingDisplay } from "@/components/shared/rating-display";
import { formatDistance } from "@/lib/utils/distance";
import { formatCurrency } from "@/lib/utils/format";
import { Search as SearchIcon, MapPin, Star, Filter } from "lucide-react";
import Link from "next/link";
import { useDebounce } from "@/hooks/use-debounce";

export default function SearchPage() {
  const { query, filters, results, isLoading, setQuery, setFilters, search } = useSearchStore();
  const [searchInput, setSearchInput] = useState(query);
  const debouncedQuery = useDebounce(searchInput, 500);

  useEffect(() => {
    setQuery(debouncedQuery);
  }, [debouncedQuery, setQuery]);

  useEffect(() => {
    search();
  }, [query, filters]);

  const handleSearch = () => {
    search();
  };

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
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : results.length === 0 ? (
        <EmptyState
          icon={<SearchIcon className="h-12 w-12 text-text-secondary" />}
          title="No providers found"
          description="Try adjusting your search criteria or filters"
        />
      ) : (
        <>
          <p className="mb-4 text-sm text-text-secondary">
            Found {results.length} provider{results.length !== 1 ? "s" : ""}
          </p>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {results.map((provider) => (
              <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-xl">{provider.businessName}</CardTitle>
                      <CardDescription className="mt-1">
                        {provider.serviceCategories.join(", ")}
                      </CardDescription>
                    </div>
                    {provider.isVerified && (
                      <Badge variant="success" className="ml-2">Verified</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {provider.rating && (
                      <RatingDisplay
                        rating={provider.rating}
                        count={provider.reviewCount}
                        size="sm"
                      />
                    )}
                    
                    <div className="flex items-center gap-2 text-sm text-text-secondary">
                      <MapPin className="h-4 w-4" />
                      <span>{provider.businessAddress.address}</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-text-secondary">
                      <span>Service Radius: {provider.serviceRadius} km</span>
                    </div>

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
