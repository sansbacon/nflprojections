# nflprojections/matching/player_matcher.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Player matching functionality for NFL projections using difflib for fuzzy string matching.
"""

from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import pandas as pd


@dataclass
class MatchResult:
    """Result of a player matching operation"""
    source1_index: int
    source2_index: int
    source1_player: Dict[str, Any]
    source2_player: Dict[str, Any]
    similarity: float
    match_fields: Dict[str, float]


class PlayerMatcher:
    """Matches players across different projection sources using fuzzy string matching"""
    
    def __init__(self, 
                 name_threshold: float = 0.7,
                 position_threshold: float = 0.8,
                 team_threshold: float = 0.5,
                 overall_threshold: float = 0.65):
        """
        Initialize PlayerMatcher with similarity thresholds
        
        Args:
            name_threshold: Minimum similarity for player names (0.0-1.0)
            position_threshold: Minimum similarity for positions (0.0-1.0)
            team_threshold: Minimum similarity for team names (0.0-1.0)
            overall_threshold: Minimum overall similarity score (0.0-1.0)
        """
        self.name_threshold = name_threshold
        self.position_threshold = position_threshold
        self.team_threshold = team_threshold
        self.overall_threshold = overall_threshold
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings for comparison
        norm_str1 = str(str1).lower().strip()
        norm_str2 = str(str2).lower().strip()
        
        return SequenceMatcher(None, norm_str1, norm_str2).ratio()
    
    def _calculate_player_similarity(self, 
                                    player1: Dict[str, Any], 
                                    player2: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate overall similarity between two player records
        
        Args:
            player1: First player record
            player2: Second player record
            
        Returns:
            Tuple of (overall_similarity, field_similarities)
        """
        field_similarities = {}
        scores = []
        weights = []
        
        # Player name comparison (highest weight)
        if 'plyr' in player1 and 'plyr' in player2:
            name_sim = self._calculate_similarity(player1['plyr'], player2['plyr'])
            field_similarities['plyr'] = name_sim
            scores.append(name_sim)
            weights.append(0.6)  # 60% weight for name
        
        # Position comparison
        if 'pos' in player1 and 'pos' in player2:
            pos_sim = self._calculate_similarity(player1['pos'], player2['pos'])
            field_similarities['pos'] = pos_sim
            scores.append(pos_sim)
            weights.append(0.2)  # 20% weight for position
        
        # Team comparison
        if 'team' in player1 and 'team' in player2:
            team_sim = self._calculate_similarity(player1['team'], player2['team'])
            field_similarities['team'] = team_sim
            scores.append(team_sim)
            weights.append(0.2)  # 20% weight for team
        
        # Calculate weighted average
        if scores and weights:
            overall_similarity = sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
        else:
            overall_similarity = 0.0
        
        return overall_similarity, field_similarities
    
    def match_players(self, 
                     source1: Union[List[Dict[str, Any]], pd.DataFrame], 
                     source2: Union[List[Dict[str, Any]], pd.DataFrame]) -> List[MatchResult]:
        """
        Match players between two data sources
        
        Args:
            source1: First data source (list of dicts or DataFrame)
            source2: Second data source (list of dicts or DataFrame)
            
        Returns:
            List of MatchResult objects for players that meet the similarity threshold
        """
        # Convert DataFrames to list of dicts if needed
        if isinstance(source1, pd.DataFrame):
            source1_data = source1.to_dict('records')
        else:
            source1_data = source1
            
        if isinstance(source2, pd.DataFrame):
            source2_data = source2.to_dict('records')
        else:
            source2_data = source2
        
        matches = []
        
        for i, player1 in enumerate(source1_data):
            for j, player2 in enumerate(source2_data):
                overall_similarity, field_similarities = self._calculate_player_similarity(player1, player2)
                
                # Check if match meets thresholds
                meets_thresholds = True
                
                # Check individual field thresholds - but be more lenient with team names
                if 'plyr' in field_similarities and field_similarities['plyr'] < self.name_threshold:
                    meets_thresholds = False
                if 'pos' in field_similarities and field_similarities['pos'] < self.position_threshold:
                    meets_thresholds = False
                # For team names, use a more lenient check since abbreviations vary widely
                if 'team' in field_similarities and field_similarities['team'] < min(self.team_threshold, 0.4):
                    meets_thresholds = False
                
                # Check overall threshold
                if overall_similarity < self.overall_threshold:
                    meets_thresholds = False
                
                if meets_thresholds:
                    matches.append(MatchResult(
                        source1_index=i,
                        source2_index=j,
                        source1_player=player1,
                        source2_player=player2,
                        similarity=round(overall_similarity, 3),
                        match_fields=field_similarities
                    ))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x.similarity, reverse=True)
        
        return matches
    
    def get_best_matches(self, 
                        source1: Union[List[Dict[str, Any]], pd.DataFrame], 
                        source2: Union[List[Dict[str, Any]], pd.DataFrame],
                        allow_duplicates: bool = False) -> List[MatchResult]:
        """
        Get the best match for each player in source1
        
        Args:
            source1: First data source
            source2: Second data source
            allow_duplicates: If False, each player from source2 can only match once
            
        Returns:
            List of best MatchResult objects, one per player in source1 (if match found)
        """
        all_matches = self.match_players(source1, source2)
        
        if not all_matches:
            return []
        
        # Group matches by source1 index
        matches_by_source1 = {}
        for match in all_matches:
            if match.source1_index not in matches_by_source1:
                matches_by_source1[match.source1_index] = []
            matches_by_source1[match.source1_index].append(match)
        
        best_matches = []
        used_source2_indices = set()
        
        for source1_index in sorted(matches_by_source1.keys()):
            # Get best match for this source1 player
            candidates = matches_by_source1[source1_index]
            
            if not allow_duplicates:
                # Filter out already used source2 players
                candidates = [m for m in candidates if m.source2_index not in used_source2_indices]
            
            if candidates:
                best_match = max(candidates, key=lambda x: x.similarity)
                best_matches.append(best_match)
                
                if not allow_duplicates:
                    used_source2_indices.add(best_match.source2_index)
        
        return best_matches
    
    def create_merged_data(self, 
                          matches: List[MatchResult],
                          merge_strategy: str = 'prefer_source1') -> List[Dict[str, Any]]:
        """
        Create merged player data from match results
        
        Args:
            matches: List of MatchResult objects
            merge_strategy: How to merge conflicting data ('prefer_source1', 'prefer_source2', 'combine')
            
        Returns:
            List of merged player records
        """
        merged_data = []
        
        for match in matches:
            if merge_strategy == 'prefer_source1':
                # Start with source1 data, add source2 projections
                merged_player = match.source1_player.copy()
                if 'proj' in match.source2_player:
                    merged_player['proj_source2'] = match.source2_player['proj']
                merged_player['match_similarity'] = match.similarity
                
            elif merge_strategy == 'prefer_source2':
                # Start with source2 data, add source1 projections
                merged_player = match.source2_player.copy()
                if 'proj' in match.source1_player:
                    merged_player['proj_source1'] = match.source1_player['proj']
                merged_player['match_similarity'] = match.similarity
                
            else:  # combine
                # Combine all non-conflicting fields
                merged_player = {}
                
                # Add all fields from source1
                for key, value in match.source1_player.items():
                    if key == 'proj':
                        merged_player['proj_source1'] = value
                    else:
                        merged_player[key] = value
                
                # Add source2 projections and any missing fields
                for key, value in match.source2_player.items():
                    if key == 'proj':
                        merged_player['proj_source2'] = value
                    elif key not in merged_player:
                        merged_player[key] = value
                
                merged_player['match_similarity'] = match.similarity
            
            merged_data.append(merged_player)
        
        return merged_data