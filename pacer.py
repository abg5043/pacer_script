#!/usr/bin/env python3
"""
GetSongBPM API Script
Search for songs by BPM, danceability, genre, and artist using GetSongBPM API
"""

import requests
import json
from typing import Optional, List, Dict
import time

class GetSongBPMClient:
    """Client for interacting with GetSongBPM API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the client with your API key
        
        Args:
            api_key: Your GetSongBPM API key
        """
        self.api_key = api_key
        self.base_url = "https://api.getsongbpm.com"
        self.headers = {
            "Accept": "application/json",
            "X-API-KEY": self.api_key
        }
    
    def search_by_tempo(self, 
                       bpm_min: int = 180, 
                       bpm_max: int = 180,
                       limit: int = 10) -> List[Dict]:
        """
        Search for songs by tempo range
        
        Args:
            bpm_min: Minimum BPM (default: 180)
            bpm_max: Maximum BPM (default: 180)
            limit: Number of results to return
            
        Returns:
            List of song dictionaries
        """
        endpoint = f"{self.base_url}/search/"
        params = {
            "bpm_min": bpm_min,
            "bpm_max": bpm_max,
            "limit": limit
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("search", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching by tempo: {e}")
            return []
    
    def search_songs(self,
                    bpm: int = 180,
                    bpm_tolerance: int = 5,
                    genre: Optional[str] = None,
                    artist: Optional[str] = None,
                    danceability_min: Optional[float] = None,
                    danceability_max: Optional[float] = None,
                    limit: int = 20) -> List[Dict]:
        """
        Advanced search for songs with multiple parameters
        
        Args:
            bpm: Target BPM (default: 180)
            bpm_tolerance: BPM tolerance range (default: 5)
            genre: Genre filter (e.g., "electronic", "rock", "pop")
            artist: Artist name filter
            danceability_min: Minimum danceability (0-1)
            danceability_max: Maximum danceability (0-1)
            limit: Number of results
            
        Returns:
            List of filtered song dictionaries
        """
        # Calculate BPM range
        bpm_min = bpm - bpm_tolerance
        bpm_max = bpm + bpm_tolerance
        
        # Build the search endpoint based on available parameters
        if artist:
            endpoint = f"{self.base_url}/artist/{artist}/tempo/{bpm_min}/{bpm_max}/"
        else:
            endpoint = f"{self.base_url}/tempo/{bpm_min}/{bpm_max}/"
        
        params = {"limit": limit}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            songs = data.get("tempo", []) if "tempo" in data else data.get("search", [])
            
            # Apply additional filters
            filtered_songs = []
            for song in songs:
                # Filter by genre if specified
                if genre and song.get("genre", "").lower() != genre.lower():
                    continue
                
                # Filter by danceability if specified
                if danceability_min is not None or danceability_max is not None:
                    danceability = song.get("danceability", 0)
                    if danceability_min and danceability < danceability_min:
                        continue
                    if danceability_max and danceability > danceability_max:
                        continue
                
                filtered_songs.append(song)
            
            return filtered_songs[:limit]
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching songs: {e}")
            return []
    
    def get_song_details(self, song_id: str) -> Dict:
        """
        Get detailed information about a specific song
        
        Args:
            song_id: The song ID from search results
            
        Returns:
            Dictionary with song details
        """
        endpoint = f"{self.base_url}/song/{song_id}/"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("song", {})
        except requests.exceptions.RequestException as e:
            print(f"Error getting song details: {e}")
            return {}
    
    def display_results(self, songs: List[Dict], verbose: bool = False):
        """
        Display search results in a formatted way
        
        Args:
            songs: List of song dictionaries
            verbose: Show all available fields
        """
        if not songs:
            print("No songs found matching your criteria.")
            return
        
        print(f"\nFound {len(songs)} songs:\n")
        print("-" * 80)
        
        for i, song in enumerate(songs, 1):
            print(f"\n{i}. {song.get('song_title', 'Unknown')} - {song.get('artist', {}).get('name', 'Unknown Artist')}")
            print(f"   BPM: {song.get('tempo', 'N/A')}")
            print(f"   Album: {song.get('album', {}).get('title', 'N/A')}")
            
            if verbose or song.get('danceability'):
                print(f"   Danceability: {song.get('danceability', 'N/A')}")
            if verbose or song.get('energy'):
                print(f"   Energy: {song.get('energy', 'N/A')}")
            if verbose or song.get('key'):
                print(f"   Key: {song.get('key', 'N/A')}")
            if verbose or song.get('genre'):
                print(f"   Genre: {song.get('genre', 'N/A')}")
            if song.get('song_id'):
                print(f"   Song ID: {song.get('song_id')}")
        
        print("-" * 80)


def main():
    """Main function to run the script"""
    
    # Configuration - UPDATE WITH YOUR API KEY
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    
    # Initialize client
    client = GetSongBPMClient(API_KEY)
    
    # Example 1: Simple search for songs at 180 BPM
    print("=" * 80)
    print("EXAMPLE 1: Songs at 180 BPM (±5 BPM tolerance)")
    print("=" * 80)
    songs = client.search_songs(
        bpm=180,
        bpm_tolerance=5,
        limit=10
    )
    client.display_results(songs)
    
    # Small delay between requests
    time.sleep(1)
    
    # Example 2: Search with danceability filter
    print("\n" + "=" * 80)
    print("EXAMPLE 2: High danceability songs at 180 BPM")
    print("=" * 80)
    danceable_songs = client.search_songs(
        bpm=180,
        bpm_tolerance=5,
        danceability_min=0.7,  # High danceability (0.7-1.0)
        limit=10
    )
    client.display_results(danceable_songs)
    
    # Small delay between requests
    time.sleep(1)
    
    # Example 3: Search by artist and BPM
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Search by specific artist")
    print("=" * 80)
    artist_songs = client.search_songs(
        bpm=180,
        bpm_tolerance=10,
        artist="Daft Punk",  # Change to your preferred artist
        limit=5
    )
    client.display_results(artist_songs, verbose=True)
    
    # Example 4: Custom search with user input
    print("\n" + "=" * 80)
    print("CUSTOM SEARCH")
    print("=" * 80)
    
    try:
        # Get user input for custom search
        user_bpm = input("Enter target BPM (default 180): ").strip()
        user_bpm = int(user_bpm) if user_bpm else 180
        
        user_tolerance = input("Enter BPM tolerance (default 5): ").strip()
        user_tolerance = int(user_tolerance) if user_tolerance else 5
        
        user_artist = input("Enter artist name (optional, press Enter to skip): ").strip()
        user_artist = user_artist if user_artist else None
        
        user_genre = input("Enter genre (optional, press Enter to skip): ").strip()
        user_genre = user_genre if user_genre else None
        
        user_danceability = input("Enter minimum danceability 0-1 (optional, press Enter to skip): ").strip()
        user_danceability = float(user_danceability) if user_danceability else None
        
        user_limit = input("Enter number of results (default 10): ").strip()
        user_limit = int(user_limit) if user_limit else 10
        
        # Perform custom search
        custom_results = client.search_songs(
            bpm=user_bpm,
            bpm_tolerance=user_tolerance,
            genre=user_genre,
            artist=user_artist,
            danceability_min=user_danceability,
            limit=user_limit
        )
        
        client.display_results(custom_results, verbose=True)
        
    except ValueError as e:
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        print("\nSearch cancelled.")


if __name__ == "__main__":
    main()