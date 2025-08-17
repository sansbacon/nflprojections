# nflprojections/projectioncombiner.py
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Eric Truett
# Licensed under the MIT License

"""
Classes for combining projections from multiple sources using various algorithms
"""

from typing import Dict, List, Optional, Callable, Tuple, Union, Any
import pandas as pd
import numpy as np
from enum import Enum

try:
    from ..matching import PlayerMatcher, MatchResult
    _HAS_MATCHING = True
except ImportError:
    _HAS_MATCHING = False


class CombinationMethod(Enum):
    """Available methods for combining projections"""
    AVERAGE = "average"
    WEIGHTED_AVERAGE = "weighted_average"
    MEDIAN = "median"
    DROP_HIGH_LOW = "drop_high_low"
    CONFIDENCE_BANDS = "confidence_bands"


class ProjectionCombiner:
    """Combines forecasts from multiple projection sources using various algorithms"""

    def __init__(self, 
                 method: CombinationMethod = CombinationMethod.AVERAGE,
                 use_fuzzy_matching: bool = False,
                 matcher_config: Optional[Dict[str, float]] = None):
        """
        Initialize projection combiner
        
        Args:
            method: Default combination method to use
            use_fuzzy_matching: Whether to use fuzzy matching for player names
            matcher_config: Configuration for PlayerMatcher thresholds
        """
        self.method = method
        self.use_fuzzy_matching = use_fuzzy_matching and _HAS_MATCHING
        
        if self.use_fuzzy_matching:
            self.player_matcher = PlayerMatcher(**(matcher_config or {}))
        else:
            self.player_matcher = None
            
        self.combination_functions = {
            CombinationMethod.AVERAGE: self._simple_average,
            CombinationMethod.WEIGHTED_AVERAGE: self._weighted_average,
            CombinationMethod.MEDIAN: self._median_combine,
            CombinationMethod.DROP_HIGH_LOW: self._drop_high_low,
            CombinationMethod.CONFIDENCE_BANDS: self._confidence_bands
        }
    
    def combine_projections(
        self, 
        projections: Union[List[pd.DataFrame], List[List[Dict[str, Any]]]], 
        method: Optional[CombinationMethod] = None,
        weights: Optional[Dict[str, float]] = None,
        player_key: str = 'plyr',
        projection_key: str = 'proj',
        **kwargs
    ) -> pd.DataFrame:
        """
        Combine projections from multiple sources
        
        Args:
            projections: List of DataFrames or Lists of dictionaries with projections
            method: Combination method to use (defaults to instance method)
            weights: Weights for weighted average (source_name -> weight)
            player_key: Column name for player identifier
            projection_key: Column name for projection values
            **kwargs: Additional method-specific parameters
            
        Returns:
            Combined projections DataFrame
        """
        if not projections:
            return pd.DataFrame()
        
        # Convert List[Dict] to DataFrame if needed
        dataframe_projections = []
        for proj in projections:
            if isinstance(proj, list):
                # Convert list of dictionaries to DataFrame
                dataframe_projections.append(pd.DataFrame(proj))
            else:
                # Already a DataFrame
                dataframe_projections.append(proj)
        
        method = method or self.method
        combination_func = self.combination_functions.get(method)
        
        if not combination_func:
            raise ValueError(f"Unknown combination method: {method}")
        
        # Merge all projections on player key
        # Merge projections using exact or fuzzy matching
        if self.use_fuzzy_matching and len(dataframe_projections) > 1:
            merged = self._merge_projections_fuzzy(dataframe_projections, player_key, projection_key)
        else:
            merged = self._merge_projections(dataframe_projections, player_key, projection_key)
        
        # Apply combination method
        result = combination_func(merged, weights=weights, **kwargs)
        
        return result
    
    def _merge_projections(
        self, 
        projections: List[pd.DataFrame], 
        player_key: str, 
        projection_key: str
    ) -> pd.DataFrame:
        """
        Merge projection DataFrames on player key
        
        Args:
            projections: List of projection DataFrames
            player_key: Column to merge on
            projection_key: Column containing projections
            
        Returns:
            Merged DataFrame with projections from all sources
        """
        if not projections:
            return pd.DataFrame()
        
        # Start with first DataFrame
        result = projections[0][[player_key, projection_key]].copy()
        result = result.rename(columns={projection_key: 'proj_0'})
        
        # Add additional projections
        for i, df in enumerate(projections[1:], 1):
            proj_df = df[[player_key, projection_key]].copy()
            proj_df = proj_df.rename(columns={projection_key: f'proj_{i}'})
            result = result.merge(proj_df, on=player_key, how='outer')
        
        return result
    
    def _merge_projections_fuzzy(
        self, 
        projections: List[pd.DataFrame], 
        player_key: str, 
        projection_key: str
    ) -> pd.DataFrame:
        """
        Merge projection DataFrames using fuzzy player matching
        
        Args:
            projections: List of projection DataFrames
            player_key: Column to merge on
            projection_key: Column containing projections
            
        Returns:
            Merged DataFrame with projections from matched sources
        """
        if not projections or not self.player_matcher:
            return pd.DataFrame()
        
        if len(projections) == 1:
            # Only one projection, no need for matching
            result = projections[0][[player_key, projection_key]].copy()
            result = result.rename(columns={projection_key: 'proj_0'})
            return result
        
        # Start with first DataFrame
        result = projections[0].copy()
        result = result.rename(columns={projection_key: 'proj_0'})
        
        # Merge each subsequent DataFrame using fuzzy matching
        for i, df in enumerate(projections[1:], 1):
            # Get best matches between result and current df
            matches = self.player_matcher.get_best_matches(
                result.to_dict('records'),
                df.to_dict('records'),
                allow_duplicates=False
            )
            
            # Create matched data
            matched_data = []
            result_indices_used = set()
            
            for match in matches:
                # Get the matched records
                result_player = result.iloc[match.source1_index].copy()
                df_player = df.iloc[match.source2_index]
                
                # Add the new projection
                result_player[f'proj_{i}'] = df_player[projection_key]
                result_player['match_similarity'] = match.similarity
                
                matched_data.append(result_player)
                result_indices_used.add(match.source1_index)
            
            # Add unmatched players from result
            for idx, player in result.iterrows():
                if idx not in result_indices_used:
                    player_copy = player.copy()
                    player_copy[f'proj_{i}'] = np.nan  # No match found
                    matched_data.append(player_copy)
            
            # Convert back to DataFrame
            if matched_data:
                result = pd.DataFrame(matched_data).reset_index(drop=True)
            else:
                # No matches found, keep original result with NaN for new projection
                result[f'proj_{i}'] = np.nan
        
        return result
    
    def _simple_average(self, merged_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Calculate simple average of projections"""
        projection_cols = [col for col in merged_df.columns if col.startswith('proj_')]
        
        # Calculate average, ignoring NaN values
        merged_df['combined_proj'] = merged_df[projection_cols].mean(axis=1, skipna=True)
        merged_df['source_count'] = merged_df[projection_cols].count(axis=1)
        
        return merged_df
    
    def _weighted_average(
        self, 
        merged_df: pd.DataFrame, 
        weights: Optional[Dict[str, float]] = None, 
        **kwargs
    ) -> pd.DataFrame:
        """Calculate weighted average of projections"""
        projection_cols = [col for col in merged_df.columns if col.startswith('proj_')]
        
        if weights is None:
            # Equal weights if none provided
            return self._simple_average(merged_df, **kwargs)
        
        # Apply weights to each projection column
        weighted_sum = pd.Series(0.0, index=merged_df.index)
        weight_sum = pd.Series(0.0, index=merged_df.index)
        
        for i, col in enumerate(projection_cols):
            weight = weights.get(f'source_{i}', 1.0)
            valid_mask = merged_df[col].notna()
            weighted_sum.loc[valid_mask] += merged_df.loc[valid_mask, col] * weight
            weight_sum.loc[valid_mask] += weight
        
        # Avoid division by zero
        merged_df['combined_proj'] = weighted_sum / weight_sum.replace(0, np.nan)
        merged_df['source_count'] = merged_df[projection_cols].count(axis=1)
        
        return merged_df
    
    def _median_combine(self, merged_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Calculate median of projections"""
        projection_cols = [col for col in merged_df.columns if col.startswith('proj_')]
        
        merged_df['combined_proj'] = merged_df[projection_cols].median(axis=1, skipna=True)
        merged_df['source_count'] = merged_df[projection_cols].count(axis=1)
        
        return merged_df
    
    def _drop_high_low(self, merged_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Calculate average after dropping highest and lowest values"""
        projection_cols = [col for col in merged_df.columns if col.startswith('proj_')]
        
        def drop_high_low_avg(row):
            values = row[projection_cols].dropna()
            if len(values) <= 2:
                return values.mean()  # Can't drop if 2 or fewer values
            
            # Drop highest and lowest
            values_sorted = values.sort_values()
            trimmed = values_sorted.iloc[1:-1]  # Remove first and last
            return trimmed.mean()
        
        merged_df['combined_proj'] = merged_df.apply(drop_high_low_avg, axis=1)
        merged_df['source_count'] = merged_df[projection_cols].count(axis=1)
        
        return merged_df
    
    def _confidence_bands(
        self, 
        merged_df: pd.DataFrame, 
        confidence_level: float = 0.95,
        **kwargs
    ) -> pd.DataFrame:
        """Calculate average with confidence bands"""
        projection_cols = [col for col in merged_df.columns if col.startswith('proj_')]
        
        # Calculate mean and standard deviation
        merged_df['combined_proj'] = merged_df[projection_cols].mean(axis=1, skipna=True)
        merged_df['proj_std'] = merged_df[projection_cols].std(axis=1, skipna=True)
        merged_df['source_count'] = merged_df[projection_cols].count(axis=1)
        
        # Calculate confidence bands
        from scipy import stats
        alpha = 1 - confidence_level
        
        def calc_confidence_bands(row):
            n = row['source_count']
            if n <= 1:
                return row['combined_proj'], row['combined_proj']
            
            std_error = row['proj_std'] / np.sqrt(n)
            t_value = stats.t.ppf(1 - alpha/2, n-1)
            margin = t_value * std_error
            
            lower = row['combined_proj'] - margin
            upper = row['combined_proj'] + margin
            
            return lower, upper
        
        confidence_bands = merged_df.apply(calc_confidence_bands, axis=1, result_type='expand')
        merged_df['proj_lower'] = confidence_bands[0]
        merged_df['proj_upper'] = confidence_bands[1]
        
        return merged_df
    
    def evaluate_combination(
        self, 
        actual_results: pd.DataFrame, 
        combined_projections: pd.DataFrame,
        player_key: str = 'plyr',
        actual_key: str = 'actual',
        projection_key: str = 'combined_proj'
    ) -> Dict[str, float]:
        """
        Evaluate the accuracy of combined projections
        
        Args:
            actual_results: DataFrame with actual performance
            combined_projections: DataFrame with combined projections
            player_key: Column for player identifier
            actual_key: Column with actual values
            projection_key: Column with projected values
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Merge actual and projected
        evaluation_df = actual_results[[player_key, actual_key]].merge(
            combined_projections[[player_key, projection_key]], 
            on=player_key, 
            how='inner'
        )
        
        if evaluation_df.empty:
            return {}
        
        actual = evaluation_df[actual_key]
        projected = evaluation_df[projection_key]
        
        # Calculate metrics
        mae = np.mean(np.abs(actual - projected))
        rmse = np.sqrt(np.mean((actual - projected) ** 2))
        mape = np.mean(np.abs((actual - projected) / actual.replace(0, np.nan))) * 100
        
        correlation = np.corrcoef(actual, projected)[0, 1] if len(actual) > 1 else 0
        
        return {
            'mean_absolute_error': mae,
            'root_mean_square_error': rmse,
            'mean_absolute_percentage_error': mape,
            'correlation': correlation,
            'sample_size': len(evaluation_df)
        }
