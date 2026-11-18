// Account, Site, and Briefing types matching init.sql and sequence diagram

export type AccountStatus = 'ACTIVE' | 'INACTIVE';
export type BriefingStatus = 'GENERATING' | 'COMPLETED' | 'FAILED' | 'BLOCKED';
export type CitationSourceType = 'PDF' | 'COMMERCIAL';
export type CitationValidationStatus = 'PENDING' | 'VALID' | 'INVALID' | 'REJECTED';

export interface Site {
    id: string;
    accountId: string;
    siteName: string;
    address: string;
}

export interface Account {
    id: string;
    legalName: string;
    taxCode: string;
    industry: string;
    status: AccountStatus;
    hasPermission: boolean; // Indicates if current user has permission scope
    sites?: Site[];
    createdAt?: string;
    updatedAt?: string;
}

export interface Citation {
    id: string;
    briefingId: string;
    citationNumber: number;
    claimText: string;
    sourceType: CitationSourceType;
    sourceExcerpt?: string;
    validationStatus: CitationValidationStatus;
}

export interface Briefing {
    id: string;
    accountId: string;
    siteId?: string | null;
    generatedBy: string;
    briefingStatus: BriefingStatus;
    isStale: boolean;
    sections: {
        companyOverview?: string;
        commercialSummary?: string;
        riskWarnings?: string[];
        recentActivities?: string[];
    };
    citations: Citation[];
    freshnessStatus: string;
    validationStatus: string;
    createdAt: string;
}

export interface AuditLog {
    id: string;
    userId: string;
    action: string;
    resourceType: string;
    resourceId: string;
    ipAddress?: string;
    metadata?: Record<string, any>;
    createdAt: string;
}
