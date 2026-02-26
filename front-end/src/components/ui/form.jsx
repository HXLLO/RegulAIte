import React from 'react';

// Form component
const Form = ({ className, ...props }) => {
  return (
    <form
      className={`space-y-6 ${className || ''}`}
      {...props}
    />
  );
};

// FormGroup component for grouping form controls
const FormGroup = ({ className, ...props }) => {
  return (
    <div
      className={`space-y-2 ${className || ''}`}
      {...props}
    />
  );
};

// FormLabel component
const FormLabel = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <label
      ref={ref}
      className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className || ''}`}
      {...props}
    />
  );
});

FormLabel.displayName = 'FormLabel';

// FormMessage component for validation messages
const FormMessage = React.forwardRef(({ className, children, ...props }, ref) => {
  return (
    <p
      ref={ref}
      className={`text-sm font-medium text-destructive ${className || ''}`}
      {...props}
    >
      {children}
    </p>
  );
});

FormMessage.displayName = 'FormMessage';

// FormDescription component
const FormDescription = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <p
      ref={ref}
      className={`text-sm text-muted-foreground ${className || ''}`}
      {...props}
    />
  );
});

FormDescription.displayName = 'FormDescription';

export { Form, FormGroup, FormLabel, FormMessage, FormDescription }; 