import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { API } from '../api'
import { toast } from '../utils/toast'
import { Search, Loader2 } from 'lucide-react'

/**
 * Search & Discovery
 * Route: /search
 * Feature Page
 */
export default function SearchAndDiscovery() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setIsSearching(true)
    try {
      const results = await API.search(searchQuery)
      setSearchResults(Array.isArray(results?.results) ? results.results : Array.isArray(results) ? results : [])
      toast.success(`Found ${Array.isArray(results?.results) ? results.results.length : Array.isArray(results) ? results.length : 0} results`)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Search failed'
      toast.error(message)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Search & Discovery</h1>
          <p className="text-muted-foreground mt-2">
            Search across your workspace and discover content
          </p>
        </div>
      </div>

      {/* Search Input */}
      <Card>
        <CardHeader>
          <CardTitle>Search</CardTitle>
          <CardDescription>Enter your search query</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for anything..."
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Button onClick={handleSearch} disabled={isSearching}>
              {isSearching ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            <CardDescription>{searchResults.length} results found</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <h3 className="font-semibold">{result.title || result.name || `Result ${index + 1}`}</h3>
                  {result.description && <p className="text-sm text-muted-foreground mt-2">{result.description}</p>}
                  {result.url && (
                    <a href={result.url} className="text-sm text-blue-500 hover:underline mt-2 block">
                      {result.url}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6">
        {/* Parameters Section */}
        <Card>
          <CardHeader>
            <CardTitle>Parameters</CardTitle>
            <CardDescription>Configure search & discovery parameters</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Parameters configuration will be implemented here.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Configuration Section */}
        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Settings and configuration options</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Configuration options will be implemented here.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Environment Section */}
        <Card>
          <CardHeader>
            <CardTitle>Environment</CardTitle>
            <CardDescription>Environment variables and settings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Environment configuration will be implemented here.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Execute Section */}
        <Card>
          <CardHeader>
            <CardTitle>Execute</CardTitle>
            <CardDescription>Run actions and operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Button>Execute</Button>
              <p className="text-sm text-muted-foreground">
                Execute functionality will be implemented here.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            <CardDescription>View results and outputs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border rounded-lg p-4">
                <p className="text-sm text-muted-foreground">
                  Results will be displayed here in a table or chart format.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
