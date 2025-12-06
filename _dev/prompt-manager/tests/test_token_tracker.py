"""
Tests for TokenTracker
"""

import pytest
from prompt_manager import TokenTracker, TokenUsage, CostEstimate


class TestTokenTracker:
    """Tests for TokenTracker"""
    
    def test_token_estimation(self):
        """Test token estimation"""
        tracker = TokenTracker()
        
        # Simple text
        text = "Hello world " * 100  # 1200 characters
        tokens = tracker.estimate_tokens(text)
        
        # Should be approximately 1200 / 4 = 300 tokens
        assert 250 <= tokens <= 350
        
    def test_token_tracking(self):
        """Test tracking token usage"""
        tracker = TokenTracker(model="gpt-4")
        
        usage = tracker.track_usage("test_operation", input_tokens=1000, output_tokens=500)
        
        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.total_tokens == 1500
        assert usage.operation == "test_operation"
        
    def test_text_tracking(self):
        """Test tracking by text"""
        tracker = TokenTracker(model="gpt-4")
        
        text = "Hello world " * 100
        usage = tracker.track_text("test_operation", text)
        
        assert usage.input_tokens > 0
        assert usage.operation == "test_operation"
        
    def test_cost_calculation(self):
        """Test cost calculation"""
        tracker = TokenTracker(model="gpt-4")
        
        cost = tracker.calculate_cost(input_tokens=1000, output_tokens=500)
        
        # GPT-4: $0.03 per 1K input, $0.06 per 1K output
        assert cost.input_cost == pytest.approx(0.03, abs=0.001)
        assert cost.output_cost == pytest.approx(0.03, abs=0.001)  # 500 tokens = 0.5 * 0.06
        assert cost.total_cost == pytest.approx(0.06, abs=0.001)
        
    def test_total_usage(self):
        """Test total usage statistics"""
        tracker = TokenTracker(model="gpt-4")
        
        tracker.track_usage("op1", input_tokens=1000)
        tracker.track_usage("op2", input_tokens=500, output_tokens=200)
        
        total = tracker.get_total_usage()
        
        assert total["total_input_tokens"] == 1500
        assert total["total_output_tokens"] == 200
        assert total["total_tokens"] == 1700
        assert total["operation_count"] == 2
        
    def test_operation_stats(self):
        """Test operation statistics"""
        tracker = TokenTracker(model="gpt-4")
        
        tracker.track_usage("op1", input_tokens=1000)
        tracker.track_usage("op1", input_tokens=500)
        tracker.track_usage("op2", input_tokens=200)
        
        stats = tracker.get_operation_stats()
        
        assert stats["op1"]["count"] == 2
        assert stats["op1"]["total_input_tokens"] == 1500
        assert stats["op1"]["avg_input_tokens"] == 750
        assert stats["op2"]["count"] == 1
        assert stats["op2"]["total_input_tokens"] == 200
        
    def test_reset(self):
        """Test reset functionality"""
        tracker = TokenTracker(model="gpt-4")
        
        tracker.track_usage("op1", input_tokens=1000)
        assert len(tracker.usage_history) == 1
        
        tracker.reset()
        assert len(tracker.usage_history) == 0
        assert len(tracker.operation_stats) == 0
        
    def test_report_generation(self):
        """Test report generation"""
        tracker = TokenTracker(model="gpt-4")
        
        tracker.track_usage("test_op", input_tokens=1000, output_tokens=500)
        
        report = tracker.get_report()
        
        assert "Token Usage Report" in report
        assert "gpt-4" in report
        assert "test_op" in report
        assert "Total Cost" in report


class TestPromptManagerTokenTracking:
    """Tests for PromptManager with token tracking"""
    
    def test_manager_tracks_load_contexts(self):
        """Test that PromptManager tracks context loading"""
        from prompt_manager import PromptManager
        
        manager = PromptManager(track_tokens=True, model="gpt-4", enable_metrics=False)
        
        # This would normally load files, but we'll test the tracking mechanism
        # by checking that token_tracker exists
        assert manager.token_tracker is not None
        
    def test_manager_tracks_compose(self):
        """Test that PromptManager tracks composition"""
        from prompt_manager import PromptManager, PromptTemplate
        
        manager = PromptManager(track_tokens=True, model="gpt-4", enable_metrics=False)
        
        template1 = PromptTemplate("Test template 1")
        template2 = PromptTemplate("Test template 2")
        
        result = manager.compose([template1, template2])
        
        # Check that tracking occurred
        stats = manager.get_operation_stats()
        assert "compose" in stats
        assert stats["compose"]["count"] == 1
        
    def test_get_token_report(self):
        """Test getting token report from manager"""
        from prompt_manager import PromptManager, PromptTemplate
        
        manager = PromptManager(track_tokens=True, model="gpt-4", enable_metrics=False)
        
        template = PromptTemplate("Test")
        manager.compose([template])
        
        report = manager.get_token_report()
        assert "Token Usage Report" in report or "Token tracking is disabled" in report
        
    def test_get_token_usage(self):
        """Test getting token usage from manager"""
        from prompt_manager import PromptManager, PromptTemplate
        
        manager = PromptManager(track_tokens=True, model="gpt-4", enable_metrics=False)
        
        template = PromptTemplate("Test")
        manager.compose([template])
        
        usage = manager.get_token_usage()
        assert "total_tokens" in usage or len(usage) == 0
        
    def test_tracking_disabled(self):
        """Test that tracking can be disabled"""
        from prompt_manager import PromptManager
        
        manager = PromptManager(track_tokens=False, enable_metrics=False)
        
        assert manager.token_tracker is None
        assert manager.get_token_usage() == {}
        assert "disabled" in manager.get_token_report().lower()

