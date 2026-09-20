import React from 'react';
import { View, Text } from 'react-native';
import { Shield } from 'lucide-react-native';
import { styles } from './TeamCard.styles';

// Matches public.teams schema in schema.sql
export interface Team {
  id: number;
  name: string;
  short_name?: string;
  symbolic_name?: string;
  primary_color?: string;
  secondary_color?: string;
  metadata?: {
    rank?: number;
    [key: string]: any;
  };
}

interface TeamCardProps {
  team: Team;
}

const TeamCard: React.FC<TeamCardProps> = ({ team }) => {
  const primaryColor = team.primary_color || '#000000';
  const secondaryColor = team.secondary_color || '#ffffffff';

  return (
    <View style={[styles.card, { borderLeftColor: primaryColor }]}>
      <View style={styles.content}>
        {/* Team Branding Icon */}
        <View style={[styles.iconContainer, { backgroundColor: secondaryColor }]}>
          <Shield size={26} color={primaryColor} />
          {team.symbolic_name && (
            <Text style={[styles.symbolicText, { color: primaryColor }]}>
              {team.symbolic_name}
            </Text>
          )}
        </View>

        {/* Team Information */}
        <View style={styles.info}>
          <Text style={styles.name}>{team.name}</Text>
          {team.short_name && (
            <Text style={styles.shortName}>{team.short_name}</Text>
          )}
        </View>
        
        {/* Optional Rank from Metadata */}
        {team.metadata?.rank && (
          <View style={styles.rankBadge}>
            <Text style={styles.rankText}>#{team.metadata.rank}</Text>
          </View>
        )}
      </View>
      
      {/* Decorative Branding Stripe */}
      <View style={[styles.stripe, { backgroundColor: primaryColor }]} />
    </View>
  );
};

export default TeamCard;