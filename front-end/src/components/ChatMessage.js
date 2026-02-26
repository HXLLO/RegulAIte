const cleanMessageContent = () => {
  if (isUser || !message.content) return message.content;
  
  let cleanedContent = message.content;
  
  // Remove internal thoughts tags
  cleanedContent = cleanedContent.replace(/<internal_thoughts>[\s\S]*?<\/internal_thoughts>/g, '');
  cleanedContent = cleanedContent.replace(/<internal[^>]*thoughts[^>]*>/g, '');
  cleanedContent = cleanedContent.replace(/<\/internal[^>]*thoughts[^>]*>/g, '');
  
  // Only handle basic formatting issues without aggressive duplicate detection
  // since the backend now handles streaming properly
  
  // Clean up excessive whitespace
  cleanedContent = cleanedContent.replace(/\s+/g, ' ').trim();
  
  // Remove multiple consecutive punctuation marks (keep intentional ones)
  cleanedContent = cleanedContent.replace(/([.!?])\1{2,}/g, '$1');
  
  // Fix obvious character repetition (like "aaa" -> "a")
  cleanedContent = cleanedContent.replace(/(\w)\1{3,}/g, '$1');
  
  return cleanedContent;
}; 