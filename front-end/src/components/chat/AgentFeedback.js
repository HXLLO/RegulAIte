import React, { useState } from 'react';
import { Box, Flex, Icon, Textarea, Button, useToast } from '@chakra-ui/react';
import { StarIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Component for providing feedback on agent responses
 */
const AgentFeedback = ({ 
  agentId, 
  sessionId, 
  messageId = null, 
  contextUsed = false,
  model = null,
  onFeedbackSubmitted = () => {} 
}) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasRated, setHasRated] = useState(false);
  
  const toast = useToast();

  // Handle star hover
  const handleStarHover = (hoveredValue) => {
    if (!hasRated) {
      setHoveredRating(hoveredValue);
    }
  };

  // Handle star click
  const handleStarClick = (selectedRating) => {
    if (!hasRated) {
      setRating(selectedRating);
      setHasRated(true);
      
      // If it's a high rating (4-5), don't expand the feedback form automatically
      // For medium to low ratings (1-3), expand to collect more feedback
      if (selectedRating <= 3) {
        setIsExpanded(true);
      } else {
        // For high ratings, submit immediately without text feedback
        submitFeedback(selectedRating);
      }
    }
  };

  // Handle feedback text change
  const handleFeedbackChange = (e) => {
    setFeedback(e.target.value);
  };

  // Submit feedback
  const submitFeedback = async (ratingToSubmit = rating) => {
    if (ratingToSubmit === 0) return;
    
    setIsSubmitting(true);
    
    try {
      const response = await axios.post(`${API_URL}/agents/feedback`, {
        agent_id: agentId,
        session_id: sessionId,
        message_id: messageId,
        rating: ratingToSubmit,
        feedback_text: feedback || null,
        context_used: contextUsed,
        model: model
      });
      
      toast({
        title: 'Feedback submitted',
        description: 'Thank you for your feedback!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Reset state
      setIsExpanded(false);
      
      // Notify parent component
      onFeedbackSubmitted({
        rating: ratingToSubmit,
        feedback: feedback,
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit feedback. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    setIsExpanded(false);
    if (!hasRated) {
      setRating(0);
    }
    setFeedback('');
  };

  return (
    <Box mt={2}>
      <Flex align="center" justify="center" direction="column">
        <Flex mb={isExpanded ? 2 : 0}>
          {[1, 2, 3, 4, 5].map((value) => (
            <Icon
              as={StarIcon}
              key={value}
              boxSize={5}
              m={1}
              cursor={hasRated ? 'default' : 'pointer'}
              color={(hoveredRating >= value || rating >= value) ? '#4415b6' : 'gray.300'}
              onMouseEnter={() => handleStarHover(value)}
              onMouseLeave={() => handleStarHover(0)}
              onClick={() => handleStarClick(value)}
            />
          ))}
        </Flex>
        
        {isExpanded && (
          <Box width="100%" mt={2}>
            <Textarea
              placeholder="Tell us more about your experience with this response..."
              value={feedback}
              onChange={handleFeedbackChange}
              size="sm"
              mb={2}
              resize="vertical"
            />
            <Flex justify="flex-end">
              <Button 
                size="xs" 
                onClick={handleCancel} 
                mr={2}
                variant="outline"
              >
                Cancel
              </Button>
              <Button 
                size="xs" 
                colorScheme="purple" 
                onClick={() => submitFeedback()}
                isLoading={isSubmitting}
              >
                Submit
              </Button>
            </Flex>
          </Box>
        )}
        
        {hasRated && !isExpanded && rating > 3 && (
          <Box fontSize="xs" color="gray.500" mt={1}>
            Thanks for your feedback!
          </Box>
        )}
        
        {hasRated && !isExpanded && rating <= 3 && (
          <Button 
            size="xs" 
            variant="link" 
            colorScheme="purple" 
            onClick={() => setIsExpanded(true)}
            mt={1}
          >
            Tell us more
          </Button>
        )}
      </Flex>
    </Box>
  );
};

export default AgentFeedback; 